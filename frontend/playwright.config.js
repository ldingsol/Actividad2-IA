// @ts-check
import { defineConfig, devices } from '@playwright/test'; // <-- ¡IMPORTAR 'devices' AQUÍ!

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directorio donde Playwright buscará tus archivos de prueba.
  testDir: './tests', 
  
  // URL base para el testing. De esta forma, page.goto('/') va a http://localhost:5173
  use: {
    // Asegúrate de que esta URL coincida con la que usa tu servidor Vite
    baseURL: 'http://localhost:5173', 
    trace: 'on-first-retry',
  },

  /* Configuración de reportería (opcional) */
  reporter: 'html',

  /* Proyectos de testing. Por defecto usa Chromium. */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
