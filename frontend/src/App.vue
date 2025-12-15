<script setup>
import AppNavigation from './components/AppNavigation.vue'; 
// Asegúrate de que la ruta sea correcta
// Si tienes más imports, déjalos aquí.
</script>

<template>
    <div>
        <AppNavigation /> 

        <main>
            <router-view />
        </main>
    </div>
</template>

<style>
/* Estilos globales que afectan a toda la aplicación */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
}
main {
    /* Mantiene el padding para que el contenido no toque los bordes */
    padding: 0 20px;
}
</style>

<style scoped>
/*
  Estos estilos solo aplicarían al contenido del template de este archivo (ej: si tuvieras un footer).
  Los estilos para la navegación están en AppNavigation.vue.
*/
</style>
