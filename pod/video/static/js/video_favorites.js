document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById("favorite-button-form");
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(form)
        fetch(form.action, {
            method: form.method,
            body: formData
        })
            .then(response => response.text()) // On récupère le contenu HTML de la réponse
            .then(data => {
                const parser = new DOMParser();
                const html = parser.parseFromString(data, 'text/html');
                const updatedButton = html.querySelector("#star_btn > i")
                const button = document.querySelector("#star_btn > i")
                button.replaceWith(updatedButton);
            })
            .catch(alert("L'ajout en favoris n'a pas pu se faire..."));
    });
});