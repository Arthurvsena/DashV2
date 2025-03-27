from nicegui import ui

def aplicar_estilo_global():
    ui.add_head_html("""
    <style>
        body, .q-page, .q-page-container {
            background-color: #0e1117 !important;
            color: #e0e0e0 !important;
            font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #e0e0e0 !important;
        }

        a {
            color: #08C5A1 !important;
            text-decoration: none;
        }

        a:hover {
            color: #00ffd5 !important;
            text-shadow: 0 0 5px #00ffd5 !important;
        }

        .plotly-graph-div text {
            fill: #e0e0e0 !important;
        }

        /* Estilização do card de login */
        .login-card {
            background-color: #161b22;
            border-radius: 18px;
            padding: 30px;
            box-shadow: 0 0 15px rgba(0, 255, 213, 0.15);
            transition: 0.3s ease;
        }

        .login-card:hover {
            box-shadow: 0 0 25px rgba(0, 255, 213, 0.25);
        }

        /* Estilo global para botões animados */
        .animated-button {
            background-color: #08C5A1;
            color: #000;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: bold;
            transition: all 0.3s ease-in-out;
        }

        .animated-button:hover {
            background-color: #00ffd5;
            box-shadow: 0 0 12px #00ffd5;
            transform: scale(1.03);
        }

        /* Estilização dos campos de input (NiceGUI/Quasar) */
        /* Estilo dos campos de input */
        .q-field__control {
            background-color: #161b22 !important;
            color: #fff !important;
            border-radius: 8px !important;
            border: 1px solid #2c2f36 !important;
            transition: 0.3s ease;
        }

        .q-field--focused .q-field__control {
            border: 1px solid #08C5A1 !important;
            box-shadow: 0 0 6px #08C5A1 !important;
        }

        .q-field__native,
        .q-field__label,
        .q-field__prefix,
        .q-field__suffix,
        .q-input__control,
        .q-placeholder {
            background-color: transparent !important;
            color: #fff !important;
        }

        /* Força o placeholder branco */
        .q-field__label {
            color: #ccc !important;
        }


        /* Loading animation */
        .loading-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(14, 17, 23, 0.9);
            backdrop-filter: blur(6px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .animate-spin {
            animation: spin 1.5s linear infinite;
        }

        .animate-pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
    """)


def estilizar_botao_animado(botao):
    botao.classes('transition duration-300 ease-in-out transform hover:scale-105 shadow-md')
    botao.style('background-color: #08C5A1; color: black;')
