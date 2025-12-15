<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

const route = useRoute();
const residentId = ref(route.params.id); // Captura el ID del residente de la URL
const payments = ref([]);
const loading = ref(true);
const error = ref(null);

const API_BASE_URL = 'http://localhost:5001/api/v1';

const fetchPaymentHistory = async () => {
    loading.value = true;
    error.value = null;

    // Llama al nuevo ENDPOINT 6
    const API_URL = `${API_BASE_URL}/dues/history/${residentId.value}`;

    try {
        const response = await axios.get(API_URL);
        payments.value = response.data.data;
    } catch (err) {
        console.error("Error al obtener historial:", err.response || err);
        error.value = "Error al cargar el historial de pagos. Verifique el backend.";
    } finally {
        loading.value = false;
    }
};

onMounted(fetchPaymentHistory);
</script>

<template>
    <div class="history-view">
        <h2>📜 Historial de Pagos (Residente ID: {{ residentId }})</h2>
        <button @click="fetchPaymentHistory" :disabled="loading" class="refresh-button">
            <span v-if="loading">Cargando...</span>
            <span v-else>Recargar Historial</span>
        </button>

        <p v-if="error" class="error-message">{{ error }}</p>
        
        <div v-if="payments.length">
            <table>
                <thead>
                    <tr>
                        <th>ID Pago</th>
                        <th>Referencia</th>
                        <th>Monto</th>
                        <th>Fecha de Registro</th>
                        <th>Estado</th>
                        <th>Procesado Por</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="pago in payments" :key="pago.id_pago">
                        <td>{{ pago.id_pago }}</td>
                        <td>{{ pago.referencia_pago }}</td>
                        <td>${{ pago.monto_pagado.toFixed(2) }}</td>
                        <td>{{ new Date(pago.fecha_pago).toLocaleDateString() }}</td>
                        <td><span :class="{'status-paid': pago.estado === 'pagado', 'status-pending': pago.estado !== 'pagado'}">{{ pago.estado.toUpperCase() }}</span></td>
                        <td>{{ pago.procesado_por }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p v-else-if="!loading">No se encontraron pagos registrados para este residente.</p>
    </div>
</template>

<style scoped>
.history-view { padding: 20px; max-width: 1000px; margin: 0 auto; }
.refresh-button { margin-bottom: 20px; padding: 10px 15px; background-color: #17a2b8; color: white; border: none; border-radius: 4px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f2f2f2; }
.status-paid { color: #1e7e34; font-weight: bold; }
.status-pending { color: #ffc107; font-weight: bold; }
.error-message { color: #dc3545; }
</style>