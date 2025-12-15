<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- Definición de Variables de Estado ---
const residentId = ref(2); // ID del residente de prueba 
const totalBalance = ref(0.00);
const monthsDue = ref(0);
const monthlyFee = ref(0.00);
const loading = ref(true);
const error = ref(null);
const generatedReference = ref(null); // Estado para guardar la referencia generada

// --- Función para Cargar el Resumen de Deuda ---
const fetchDuesSummary = async () => {
    loading.value = true;
    error.value = null;
    
    // CORREGIDO: Se usa el puerto 5001
    const API_URL = `http://localhost:5001/api/v1/dues/summary/${residentId.value}`; 

    try {
        const response = await axios.get(API_URL);
        const data = response.data;
        
        // Asegurarse de que los valores sean números antes de la asignación
        totalBalance.value = parseFloat(data.total_balance) || 0.00;
        monthsDue.value = parseInt(data.months_due) || 0;
        monthlyFee.value = parseFloat(data.monthly_fee) || 0.00;
        
    } catch (err) {
        console.error("Error fetching data:", err);
        error.value = "No se pudo conectar al API de pagos o la solicitud falló.";
        totalBalance.value = 0.00;
        monthsDue.value = 0;

    } finally {
        loading.value = false;
    }
};

// --- Función para Solicitar Referencia de Pago ---
const requestReference = async () => {
    // CORREGIDO: Se usa el puerto 5001
    const API_URL = `http://localhost:5001/api/v1/dues/request-reference`;

    try {
        const response = await axios.post(API_URL, {
            id_residente: residentId.value,
            monto_a_pagar: totalBalance.value // Pagar el saldo total
        });

        // Guardar la referencia recibida del backend
        generatedReference.value = response.data.referencia_pago;

        alert(`Referencia generada: ${response.data.referencia_pago}\nPor favor, preséntala en la caja.`);

    } catch (err) {
        console.error("Error al generar referencia:", err.response ? err.response.data : err);
        error.value = "🔴 Error al generar la referencia de pago.";
    }
};

// Llamar a la función cuando el componente se monte (cargue)
onMounted(fetchDuesSummary);

</script>

<template>
    <div class="dues-payment-view">
        <h1>Control de Pagos de Cuotas (Residente ID: {{ residentId }})</h1>

        <div v-if="loading" class="loading-state">
            Cargando resumen de deuda...
        </div>

        <div v-else-if="error" class="error-state">
            <p>🔴 {{ error }}</p>
            <button @click="fetchDuesSummary">Reintentar</button>
        </div>

        <div v-else class="summary-card">
            <h2>Resumen de Saldo Pendiente</h2>
            <p>Cuota Mensual Base: **${{ monthlyFee.toFixed(2) }}**</p>
            <p>Meses Adeudados: **{{ monthsDue }}**</p>
            <h3>Saldo Total Pendiente: **${{ totalBalance.toFixed(2) }}**</h3>
            
            <hr>
            
            <div class="payment-options">
                <h3>Opciones de Pago en Caja:</h3>
                <p>Monto a pagar: ${{ totalBalance.toFixed(2) }}</p>
                <button class="pay-button" @click="requestReference" :disabled="loading">
                    Generar Referencia de Pago en Caja
                </button>
            </div>

            <div v-if="generatedReference" class="reference-info">
                <p>✅ **Referencia para Caja:** <strong>{{ generatedReference }}</strong>
                </p>
                <p>Lleve este código a la caja de la administración para completar el pago.</p>
            </div>
        </div>
    </div>
</template>


<style scoped>
.dues-payment-view { padding: 20px; max-width: 800px; margin: 0 auto; }
.summary-card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; background-color: #f9f9f9; }
.error-state { color: red; }
.pay-button { 
    background-color: #007bff; color: white; padding: 10px 15px; border: none; 
    border-radius: 5px; cursor: pointer; margin-top: 10px; 
}
.reference-info {
    margin-top: 20px;
    padding: 10px;
    background-color: #e6ffe6;
    border: 1px solid #00cc00;
    border-radius: 4px;
}
</style>