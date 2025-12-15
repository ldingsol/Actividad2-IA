import { createRouter, createWebHistory } from 'vue-router';
// Importamos la vista que ya creamos para el control de pagos
import DuesPaymentView from '../views/DuesPaymentView.vue';
// Importamos otras vistas que la aplicación podría necesitar (asumidas)
import DashboardView from '../views/DashboardView.vue';
import AdminView from '../views/AdminView.vue'; 
import CashierView from '../views/CashierView.vue' // Importar la nueva vista
import PaymentHistoryView from '../views/PaymentHistoryView.vue'; // Asegúrate que la ruta sea correcta
import ResidentRegistrationView from '../views/ResidentRegistrationView.vue'; // Verifica la ruta

// --- DEFINICIÓN CORRECTA DEL ARRAY DE RUTAS ---
const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: DashboardView,
        meta: { title: 'Resumen Principal' }
    },
    {
        // Ruta principal para el control y pago de cuotas del residente
        path: '/dues', 
        name: 'DuesPayment',
        component: DuesPaymentView,
        meta: { title: 'Pago de Cuotas' }
    },
    {
        // Ruta para el módulo del cajero/administrador (registro de pagos en efectivo)
        path: '/admin/cash-register', 
        name: 'CashRegister',
        component: AdminView,
        meta: { title: 'Registro de Caja', requiresAuth: true, roles: ['admin', 'cajero'] }
    },
    // CORRECCIÓN: La ruta /cashier DEBE estar dentro del array 'routes'
    {
        path: '/cashier', // URL para acceder: http://localhost:5173/cashier
        name: 'cashier',
        component: CashierView,
        meta: { title: 'Módulo de Cajero' } // Añadido título
    },
    // Aquí se podrían añadir más rutas como /reports, /profile, etc.
    {
        path: '/history/:id', // Usa :id para capturar el ID del residente
        name: 'payment-history',
        component: PaymentHistoryView
    },
    {
        path: '/admin/register', 
        name: 'register-resident',
        component: ResidentRegistrationView
    }
];
// ---------------------------------------------------

const router = createRouter({
    // Usa la historia basada en el navegador (URLs limpias sin #)
    history: createWebHistory(), 
    routes: routes // Sintaxis correcta: { key: value }
});

// Opcional: Hook de navegación para actualizar el título de la página
router.beforeEach((to, from, next) => {
    document.title = to.meta.title || 'Control de Pagos Urbanización';
    next();
});

export default router;