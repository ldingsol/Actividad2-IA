<script setup>
import { ref } from 'vue';

// ID de Residente de prueba para los enlaces de Residente
const residentId = ref(2); 

// Puedes cambiar esta variable para probar con otro ID de residente (ej: 1000)
// Nota: En una aplicación real, este ID vendría del estado de autenticación.
</script>

<template>
    <nav class="app-navbar">
        <router-link to="/" class="nav-brand">SISTEMA DE GESTIÓN DE CUOTAS</router-link>
        
        <div class="nav-links">
            <div class="nav-group">
                <span>Residente (ID {{ residentId }})</span>
                <router-link :to="`/dues/${residentId}`">💳 Ver/Pagar Cuotas</router-link>
                <router-link :to="`/history/${residentId}`">📜 Historial de Pagos</router-link>
            </div>

            <div class="nav-group">
                <span>Administración</span>
                <router-link to="/cashier">💰 Módulo Cajero</router-link>
                <router-link to="/admin/register">🔑 Registrar Residente</router-link>
                <router-link to="/admin/generate-dues">⚙️ Generar Cuotas Masivas</router-link>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.app-navbar {
    background-color: #343a40; /* Color oscuro para el fondo */
    color: white;
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    margin-bottom: 20px; /* Separar del contenido principal */
}

.nav-brand {
    font-size: 1.5em;
    font-weight: bold;
    color: #ffc107; /* Amarillo de destaque */
    text-decoration: none;
    padding-right: 30px;
}

.nav-links {
    display: flex;
    gap: 25px;
}

.nav-group {
    display: flex;
    flex-direction: column;
    padding-right: 15px;
    border-right: 1px solid #495057; /* Separador de grupos */
}
.nav-group:last-child {
    border-right: none;
    padding-right: 0;
}

.nav-group span {
    font-weight: bold;
    color: #adb5bd; /* Gris claro para el título del grupo */
    margin-bottom: 5px;
    font-size: 0.85em;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 3px 0;
    transition: color 0.2s;
}

.nav-links a:hover, .nav-links a.router-link-exact-active {
    color: #28a745; /* Verde para hover y activo */
    text-decoration: underline;
}
</style>