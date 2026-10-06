document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById(
                "plan-form"
            );

        const button =
            document.getElementById(
                "generate-btn"
            );


        if (form && button) {

            form.addEventListener(
                "submit",
                function () {

                    button.disabled = true;

                    button.textContent =
                        "Generating...";

                }
            );

        }

    }
);