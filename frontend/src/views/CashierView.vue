<template>
    <div class="cashier-view">
        <h1>Módulo de Caja (Procesamiento de Pagos)</h1>
        <p class="instruction-text">
            Ingrese la referencia generada por el residente para verificar el monto y aplicar el pago en efectivo.
        </p>
        
        <div class="search-box">
            <input 
                type="text" 
                v-model="searchReference" 
                placeholder="Ingrese la Referencia de Pago (Ej: REF-2-1700...)"
                :disabled="loading"
            />
            <button @click="searchPayment" :disabled="loading || !searchReference.trim()">
                <span v-if="loading">Buscando...</span>
                <span v-else>Buscar Referencia</span>
            </button>
        </div>

        <p v-if="error" class="error-message">❌ {{ error }}</p>
        <p v-if="loading && !paymentDetails" class="loading-state">Cargando detalles de la referencia...</p>
        <p v-if="successMessage" class="success-message">✅ {{ successMessage }}</p>

        <div v-if="paymentDetails" class="payment-card">
            <h2>Detalles de la Transacción Pendiente</h2>
            <p><strong>Referencia:</strong> {{ paymentDetails.referencia_pago }}</p>
            <p><strong>Monto Solicitado:</strong> ${{ paymentDetails.monto_pagado.toFixed(2) }}</p>
            <hr>
            <h3>Datos del Residente</h3>
            <p><strong>Nombre:</strong> {{ paymentDetails.residente_nombre }}</p>
            <p><strong>Cédula:</strong> {{ paymentDetails.residente_cedula }}</p>
            
            <button class="confirm-button" @click="processCashPayment" :disabled="loading">
                <span v-if="loading">Procesando Pago...</span>
                <span v-else>CONFIRMAR PAGO EN EFECTIVO</span>
            </button>

            <div v-if="processResult.id_pago" class="result-details">
                <p>ID de Pago Registrado: <strong>{{ processResult.id_pago }}</strong></p>
                <p>Cuotas Aplicadas: <strong>{{ processResult.cuotas_aplicadas }}</strong></p>
                <p class="unapplied" v-if="processResult.remaining_unapplied > 0">
                    Cambio/Restante NO aplicado: <strong>${{ processResult.remaining_unapplied.toFixed(2) }}</strong>
                </p>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api/v1';

// --- Estado de la Vista ---
const searchReference = ref(''); // Input del cajero
const paymentDetails = ref(null); // Datos del pago pendiente
const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);
const cashierId = ref(1); // ID fijo del cajero para pruebas
const processResult = reactive({ // Resultado de la aplicación de pago
    id_pago: null,
    cuotas_aplicadas: 0,
    remaining_unapplied: 0.00,
});

// --- Funciones de Búsqueda y Procesamiento ---

const searchPayment = async () => {
    loading.value = true;
    error.value = null;
    successMessage.value = null;
    paymentDetails.value = null;
    processResult.id_pago = null; // Reiniciar resultados anteriores

    if (!searchReference.value.trim()) {
        error.value = "Debe ingresar una referencia de pago.";
        loading.value = false;
        return;
    }

    // Llama al ENDPOINT 5: /admin/search-pending-payment/<referencia>
    const API_URL = `${API_BASE_URL}/admin/search-pending-payment/${searchReference.value}`;

    try {
        const response = await axios.get(API_URL);
        // La data viene en response.data.data según el Endpoint 5
        paymentDetails.value = response.data.data;

    } catch (err) {
        console.error("Error al buscar referencia:", err.response ? err.response.data : err);
        error.value = err.response?.data?.error || "Error al buscar la referencia. Verifique el código.";
    } finally {
        loading.value = false;
    }
};

const processCashPayment = async () => {
    if (!paymentDetails.value || !confirm(`¿Confirmar el pago de $${paymentDetails.value.monto_pagado.toFixed(2)} para el residente ${paymentDetails.value.residente_nombre}?`)) {
        return;
    }
    
    loading.value = true;
    error.value = null;
    successMessage.value = null;
    
    // Llama al ENDPOINT 3: /admin/register-cash-payment
    const API_URL = `${API_BASE_URL}/admin/register-cash-payment`;
    
    try {
        const payload = {
            referencia_pago: paymentDetails.value.referencia_pago,
            monto_pagado: paymentDetails.value.monto_pagado,
            id_cajero: cashierId.value,
            id_residente_pagador: paymentDetails.value.id_residente
        };

        const response = await axios.post(API_URL, payload);

        successMessage.value = `Pago de ${paymentDetails.value.monto_pagado.toFixed(2)} procesado con éxito.`;
        
        // Almacenar resultados
        processResult.id_pago = response.data.id_pago;
        processResult.cuotas_aplicadas = response.data.cuotas_aplicadas;
        processResult.remaining_unapplied = response.data.remaining_unapplied;

        // Limpiar la vista y recargar el estado para evitar doble pago
        // paymentDetails.value = null;
        // searchReference.value = ''; // Opcional: mantener la referencia visible para auditoría

    } catch (err) {
        console.error("Error al procesar pago:", err.response || err);
        error.value = err.response?.data?.error || "🔴 Error al procesar el pago. Consulte el log.";
        successMessage.value = null;
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.cashier-view { padding: 20px; max-width: 900px; margin: 0 auto; }
.instruction-text { color: #666; margin-bottom: 20px; }
.search-box { display: flex; gap: 10px; margin-bottom: 20px; }
.search-box input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.search-box button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
.search-box button:hover:not(:disabled) { background-color: #0056b3; }

.payment-card { border: 2px solid #007bff; padding: 25px; border-radius: 8px; background-color: #e9f7ff; margin-top: 20px; }
.payment-card h2 { color: #007bff; border-bottom: 1px solid #b3d9ff; padding-bottom: 10px; margin-top: 0; }
.payment-card hr { border-top: 1px dashed #b3d9ff; margin: 15px 0; }

.confirm-button { width: 100%; padding: 15px; background-color: #28a745; color: white; border: none; border-radius: 4px; font-size: 1.1em; margin-top: 15px; cursor: pointer; transition: background-color 0.3s; }
.confirm-button:hover:not(:disabled) { background-color: #1e7e34; }

.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; font-weight: bold; }
.success-message { color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 4px; font-weight: bold; }
.loading-state { color: #007bff; font-style: italic; }
.result-details { border-top: 1px solid #b3d9ff; margin-top: 15px; padding-top: 10px; }
.unapplied { color: #856404; font-weight: bold; }
</style>

