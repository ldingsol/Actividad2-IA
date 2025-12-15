<script setup>
import { ref } from 'vue';
import axios from 'axios';

const resident = ref({
    nombre_completo: '',
    cedula: '',
    telefono: '',
    email: '',
    codigo_llave: '',
});

const loading = ref(false);
const error = ref(null);
const successMessage = ref(null);
const newResidentId = ref(null); // Variable para almacenar el ID devuelto por Flask

const API_BASE_URL = 'http://localhost:5001/api/v1';

const registerResident = async () => {
    loading.value = true;
    error.value = null;
    successMessage.value = null;
    newResidentId.value = null; // Limpiar ID anterior

    // Validación básica
    if (!Object.values(resident.value).every(val => val.trim())) {
        error.value = "Por favor, complete todos los campos obligatorios.";
        loading.value = false;
        return;
    }

    const API_URL = `${API_BASE_URL}/admin/register-resident`;

    try {
        const response = await axios.post(API_URL, resident.value);
        
        // --- CAPTURA Y VISUALIZACIÓN DEL ID ---
        newResidentId.value = response.data.id_residente; 
        
        successMessage.value = `✅ Residente y Llave #${response.data.num_llave} registrados con éxito.`;
        // ----------------------------------------
        
        // Limpiar formulario después del éxito
        resident.value = { nombre_completo: '', cedula: '', telefono: '', email: '', num_llave: '' };
        
    } catch (err) {
        console.error("Error al registrar residente:", err.response ? err.response.data : err);
        error.value = err.response?.data?.error || "🔴 Error al registrar. Consulte el log de Flask.";
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <div class="registration-view">
        <h1>🔑 Registro de Nuevo Residente y Llave de Acceso</h1>
        <p class="instruction-text">Complete los datos para dar de alta al residente y asignarle una nueva llave de acceso.</p>

        <form @submit.prevent="registerResident" class="registration-form">
            
            <h3>Información Personal</h3>
            <div class="form-group">
                <label for="nombre_completo">Nombre Completo:</label>
                <input type="text" id="nombre_completo" v-model="resident.nombre_completo" required>
            </div>
            <div class="form-group">
                <label for="cedula">Cédula / ID:</label>
                <input type="text" id="cedula" v-model="resident.cedula" required>
            </div>
            <div class="form-group">
                <label for="telefono">Teléfono:</label>
                <input type="text" id="telefono" v-model="resident.telefono" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" v-model="resident.email" required>
            </div>

            <h3>Asignación de Llave</h3>
            <div class="form-group">
                <label for="codigo_llave">Número de Llave:</label>
                <input type="text" id="codigo_llave" v-model="resident.num_llave" required>
                <small>Ej: Apto 101, Casa 5, etc. Debe ser único.</small>
            </div>

            <p v-if="error" class="error-message">❌ {{ error }}</p>
            <div v-if="successMessage" class="success-message-box">
                <p>{{ successMessage }}</p>
                <p v-if="newResidentId" class="assigned-id">
                    <strong>ID ASIGNADO: #{{ newResidentId }}</strong>
                </p>
            </div>

            <button type="submit" :disabled="loading" class="submit-button">
                <span v-if="loading">Registrando...</span>
                <span v-else>Registrar Residente y Llave</span>
            </button>
        </form>
    </div>
</template>

<style scoped>
.registration-view { padding: 20px; max-width: 600px; margin: 0 auto; }
.instruction-text { color: #666; margin-bottom: 25px; }
.registration-form { background: #f9f9f9; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.registration-form h3 { margin-top: 0; color: #007bff; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }

.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-group small { display: block; margin-top: 5px; color: #888; font-size: 0.9em; }

.submit-button { width: 100%; padding: 12px; background-color: #28a745; color: white; border: none; border-radius: 4px; font-size: 1.1em; margin-top: 20px; cursor: pointer; transition: background-color 0.3s; }
.submit-button:hover:not(:disabled) { background-color: #1e7e34; }

.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; font-weight: bold; }

.success-message-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 15px;
    border-radius: 4px;
    margin-top: 15px;
}
.success-message-box p {
    margin: 0;
    color: #155724;
    font-weight: bold;
}
.assigned-id {
    margin-top: 5px !important;
    font-size: 1.2em;
    color: #007bff; /* Destacar el ID en azul */
}
</style>