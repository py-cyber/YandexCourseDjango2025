document.addEventListener("DOMContentLoaded", function () {
    document.querySelector('.js-only').style.display = 'block';

    const server_time = new Date(document.getElementById("year").dataset.time.replace(' ', 'T'));
    const client_time = new Date();

    const delta_time = Math.abs(client_time - server_time);

    if (delta_time <= 24 * 60 * 60 * 1000) {
        const client_year = client_time.getFullYear();
        document.getElementById("year").textContent = client_year;
    }
});