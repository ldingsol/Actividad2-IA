// @ts-check
import { test, expect } from '@playwright/test';

// Datos únicos basados en el tiempo para evitar conflictos en cada ejecución
const UNIQUE_ID = `TEST-${Date.now()}`;
const TEST_AMOUNT = 50.00; // Monto fijo de la cuota
let residentId; // Almacenará el ID generado por el sistema
let paymentReference; // Almacenará la referencia generada por el residente

// URL base de la aplicación Vue

const BASE_URL = 'http://localhost:5173';
// URL base de la API Flask (asumiendo que corre en el puerto 5001)
const API_BASE_URL = 'http://localhost:5001/api/v1'; 

test.describe('Flujo de Pago Aislado: Registro, Cuota API y Pago', () => {

    test('1. Registro de Nuevo Residente y Generación de Cuota Vía API', async ({ page }) => {
        
        // --- A. REGISTRO DE RESIDENTE (VÍA GUI) ---
        await test.step('A. Registrar un nuevo residente de prueba', async () => {
            await page.goto(`${BASE_URL}/admin/register`);

            // Rellenar formulario con datos únicos
            await page.fill('input#nombre_completo', `Residente ${UNIQUE_ID}`);
            await page.fill('input#cedula', UNIQUE_ID);
            await page.fill('input#telefono', '5551234');
            await page.fill('input#email', `test.${UNIQUE_ID}@mail.com`);
            await page.fill('input#num_llave', UNIQUE_ID.slice(-4)); // Usamos los últimos 4 dígitos

            await page.click('button.submit-button');

            // Esperar mensaje de éxito y extraer el ID
            const successMessage = await page.textContent('.success-message-box');
            expect(successMessage).toContain('registrados con éxito');
            
            // Extraer el ID asignado por el Backend/DB
            const idText = await page.textContent('.assigned-id');
            residentId = idText.match(/#(\d+)/)[1];
            expect(residentId).toBeDefined();
            console.log(`✅ Residente registrado con ID: ${residentId}`);
        });

        // --- B. GENERACIÓN DE CUOTA (VÍA API DIRECTA) ---
        await test.step('B. Generar una cuota de $60.00 usando el endpoint de la API', async () => {
            
            // Usamos el APIRequestContext de Playwright para saltarnos el Frontend
            const api = page.request;

            const response = await api.post(`${API_BASE_URL}/admin/generate-monthly-dues`, {
                data: {
                    monto: TEST_AMOUNT,
                    descripcion: `Cuota Única de Test ${UNIQUE_ID}`,
                },
            });

            // Verificar que la API respondió con éxito
            expect(response.ok()).toBeTruthy();
            const jsonResponse = await response.json();
            
            // En lugar de verificar muchas cuotas, verificamos que el proceso fue exitoso
            expect(jsonResponse.message).toContain('Cuotas mensuales generadas con éxito.');
            console.log(`✅ Cuota generada VÍA API. Total Cuotas Creadas: ${jsonResponse.total_cuotas_creadas}`);
        });
    });

    test('2. Flujo de Pago: Generar Referencia y Procesar en Caja', async ({ page }) => {
        // Asegurarse de que el ID se haya obtenido en el paso anterior
        if (!residentId) {
            test.skip(); 
            return;
        }

        // --- A. RESIDENTE: VER DEUDA Y GENERAR REFERENCIA ---
        await test.step('A. Generar una referencia de pago para la cuota', async () => {
            await page.goto(`${BASE_URL}/dues/${residentId}`);
            
            // Debe haber una cuota del monto de TEST_AMOUNT ($60.00) pendiente
            expect(await page.textContent('.debt-total-amount')).toContain(TEST_AMOUNT.toFixed(2));

            // Clic en el botón de la cuota pendiente (asumimos que solo hay una pendiente)
            // Esperamos que la cuota de $60.00 esté visible antes de hacer clic.
            await page.waitForSelector(`.due-item-pending:has-text("${TEST_AMOUNT.toFixed(2)}")`);
            await page.click(`.due-item-pending:has-text("${TEST_AMOUNT.toFixed(2)}") button`); 

            // Esperar que aparezca el modal/sección de generación de referencia
            await page.waitForSelector('.reference-section');

            // Clic en el botón de generar referencia
            await page.click('button.generate-ref-button'); 

            // Extraer la referencia generada
            const refText = await page.textContent('.reference-number');
            paymentReference = refText.match(/REF-\d+-\d+/)[0];
            expect(paymentReference).toMatch(/^REF-\d+-\d+$/);
            console.log(`✅ Referencia de pago generada: ${paymentReference}`);
        });

        // --- B. CAJERO: BUSCAR Y REGISTRAR PAGO EN EFECTIVO ---
        await test.step('B. Procesar pago en efectivo en el Módulo Cajero', async () => {
            await page.goto(`${BASE_URL}/cashier`);

            // 1. Buscar la referencia
            await page.fill('input#reference-input', paymentReference);
            await page.click('button.search-button');

            // Esperar que se muestre la información de la referencia (monto y cuotas)
            await page.waitForSelector('.payment-details');

            // 2. Confirmar el pago 
            await page.fill('input#cashier-id', '1'); // ID del cajero de prueba
            await page.click('button.confirm-payment-button');

            // Verificar mensaje de éxito
            const successText = await page.textContent('.success-message');
            expect(successText).toContain('El pago en efectivo fue registrado con éxito');
            console.log(`✅ Pago procesado correctamente.`);
        });
    });

    test('3. Validación Final: Deuda Cero e Historial Actualizado', async ({ page }) => {
        // Asegurarse de que el ID se haya obtenido
        if (!residentId) {
            test.skip();
            return;
        }

        // --- A. VALIDAR DEUDA CERO ---
        await test.step('A. Validar que el residente no tiene deuda pendiente', async () => {
            await page.goto(`${BASE_URL}/dues/${residentId}`);
            
            // La deuda debe ser $0.00
            expect(await page.textContent('.debt-total-amount')).toContain('0.00');

            // La tabla de cuotas no debe tener items pendientes
            const pendingItemsCount = await page.locator('.due-item-pending').count();
            expect(pendingItemsCount).toBe(0);
            console.log(`✅ Deuda validada en $0.00.`);
        });

        // --- B. VALIDAR HISTORIAL DE PAGOS ---
        await test.step('B. Validar que el pago aparece en el historial', async () => {
            await page.goto(`${BASE_URL}/history/${residentId}`);

            // Esperar a que la tabla cargue
            await page.waitForSelector('table');
            
            // Buscar la referencia de pago y el estado 'PAGADO'
            const pagoRow = page.locator('table tbody tr', { hasText: paymentReference });
            
            // La fila debe existir y contener el estado PAGADO y el monto correcto
            await expect(pagoRow).toBeVisible();
            await expect(pagoRow).toContainText('PAGADO');
            await expect(pagoRow).toContainText(TEST_AMOUNT.toFixed(2));

            console.log(`✅ Pago encontrado en el historial.`);
        });
    });
});