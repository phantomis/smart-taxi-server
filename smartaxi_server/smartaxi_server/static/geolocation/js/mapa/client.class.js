/**
 * Created with PyCharm.
 * User: phantomis
 * Date: 15-06-13
 * Time: 21:38
 * To change this template use File | Settings | File Templates.
 */
(function (window, undefined) {

    var Client = (function () {

        // Config
        var config = {
            refreshRate: 600000 // 10 minutos
        };

        // Ambito privado
        var privado = {

            // Init
            init: function () {

            },

            getProgramasPorDia: function (fechaDia) {

            },

            // Recupera la informacion de ultimos programas y el dia actual
            getUltimosProgramas: function () {

            },

            // Procesos y manipulacion de data
            process: {

                // Ultimos programas
                ultimosProgramas: {
                    refresh: function (programas) {

                    },
                    molde: function (programa) {

                    },

                    eventualizaCarrusel: function () {

                    }
                },

                // Programacion por dia
                programacionPorDia: {
                    refresh: function (data) {

                    },
                    molde: function (programa) {

                    },
                    actualizarSelectorDias: function (dias) {

                    }
                }
            }
        };

        // Ambito publico
        return {
            init: function () {
                privado.init();
            }
        };
    })();

    window.Client = Client;
})(window);


