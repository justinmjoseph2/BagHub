const ctx = document.getElementById("myPieChart").getContext("2d");
const myPieChart = new Chart(ctx, {
    type: "pie",
    data: {{ chart_data|safe }},
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "top",
            },
            title: {
                display: true,
                text: "Product Demand",
            },
        },
    },
});