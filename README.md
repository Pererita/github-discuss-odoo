# Integración de GitHub con Odoo Discuss

Este módulo integra los eventos de un repositorio de GitHub con el módulo de "Conversaciones" (Discuss) de Odoo, permitiendo un monitoreo eficiente de la actividad del repositorio directamente desde Odoo.

## Descripción

La integración funciona mediante un webhook configurado en el repositorio de GitHub. Cuando ocurren eventos (como pushes, pull requests, etc.), GitHub envía una notificación a un endpoint específico en Odoo. Este módulo procesa esa notificación y publica un mensaje formateado en un canal de Conversaciones predefinido.

## Características

-   Recepción de eventos de GitHub a través de webhooks.
-   Publicación de notificaciones en canales de Odoo Discuss.
-   Configuración segura de credenciales y parámetros sensibles.

## Configuración

Para que la integración funcione correctamente, sigue estos pasos:

### 1. Configuración de Parámetros del Sistema

Este módulo utiliza parámetros del sistema para manejar datos sensibles como credenciales de API o identificadores. Esto evita que información crítica se guarde directamente en el código, utilice el archivo `.env.example` para saber cuales debe crear.

### 2. Configuración del Webhook en GitHub

1.  Ve a la configuración de tu repositorio en GitHub (`Settings` > `Webhooks`).
2.  Haz clic en `Add webhook`.
3.  En **Payload URL**, introduce la URL del endpoint en tu instancia de Odoo. Típicamente será algo como: `https://tu-dominio.odoo.com/github/webhook`.
4.  En **Content type**, selecciona `application/json`.
5.  En **Secret**, introduce el mismo valor que pusiste en la variable `GITHUB_WEBHOOK_SECRET` de tu archivo `.env`. Esto es crucial para asegurar que las peticiones vienen de GitHub.
6.  Selecciona los eventos que quieres que disparen el webhook.
    - Branch or tag creation
    - Branch or tag deletion
    - Deployment statuses
    - Issue comments
    - Issues
    - Pull request review comments
    - Pull request reviews
    - Pull requests
    - Pushes
    - Workflow runs
7.  Asegúrate de que el webhook esté activo (`Active`).

## Uso

Una vez configurado, cualquier evento seleccionado en el webhook de GitHub generará automáticamente un mensaje en el canal de Odoo Discuss especificado. Esto permite al equipo mantenerse informado sobre la actividad del repositorio sin salir de Odoo.
