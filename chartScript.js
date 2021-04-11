// window.onload = function () {
//     autocomplete(document.getElementById("symbol_input"), symbols)
//     .then(v => {
//         var form = document.getElementById('stock_chart');
//         console.log(form);
//         form.addEventListener("submit", function(e) {
//             e.preventDefault();
//             const formData = new FormData(e.target);
//             var value = formData.get('symbol')
//             var isValid = false;

//             var labels = []
//             var prices = []

//             // symbols & token defined in autocomplete.js
//             if (symbols.includes(value)) {
//                 isValid = true;
//             }

//             if (!isValid){
//                 alert("Please give a valid input");
//                 return false;
//             }
//             else {
//                 var url = `https://cloud.iexapis.com/stable/stock/${value}/chart/ytd?chartCloseOnly=true&token=${tk}`
//                 fetch(url)
//                 .then (response => {
//                     if (!response.ok) {
//                         throw new Error("HTTP error "+response.status);
//                     } return response.json();
//                 })
//                 .then (val => {
//                     val.forEach(function (a) {
//                         prices.push(a.close);
//                         labels.push(a.date);
//                     })
//                 })
//                 .then (p => {
//                     const data2 = {
//                         labels: labels,
//                         datasets: [{
//                             label: value,
//                             data: prices,
//                             fill: false, 
//                             borderColor: 'rgb(75, 192, 192)',
//                             tension: 0.1
//                         }]
//                     }
//                     // clunky canvas cleanup to allow different stocks to load
//                     var oldcanv = document.getElementById('myChart');
//                     document.getElementById('chart').removeChild(oldcanv);
//                     var canv = document.createElement('canvas');
//                     canv.id = 'myChart';
//                     document.getElementById('chart').appendChild(canv);

//                     var ctx = document.getElementById('myChart').getContext('2d');
//                     var myLineChart = new Chart(ctx, {
//                         type: 'line',
//                         data: data2,
//                         options: {
//                             animations: {
//                                 tension: {
//                                     duration: 1000,
//                                     easing: 'linear',
//                                     from: 1,
//                                     to: 0,
//                                     loop: false
//                                 }
//                             },
//                             scales: {
//                                 y: {
//                                     suggestedMin: Math.min.apply(Math, prices) * 0.9,
//                                     suggestedMax: Math.max.apply(Math, prices) * 1.05
//                                 }
//                             }
//                         }
//                     }); 
//                 })
//                 .catch(err => {
//                     throw new Error("Symbol processing failed "+err);
//                 })
//             }
//         })
//     })


var form = document.getElementById("stock_chart");
console.log(form);
form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    var value = formData.get('symbol')
    var isValid = false;

    var labels = []
    var prices = []

    // symbols & tk defined in autocomplete.js
    if (symbols.includes(value)) {
        isValid = true;
    }

    if (!isValid) {
        alert("Please give a valid input");
        return false;
    }
    else {
        var url = `https://cloud.iexapis.com/stable/stock/${value}/chart/ytd?chartCloseOnly=true&token=${tk}`
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("HTTP error " + response.status);
                } return response.json();
            })
            .then(val => {
                val.forEach(function (a) {
                    prices.push(a.close);
                    labels.push(a.date);
                })
            })
            .then(p => {
                const data2 = {
                    labels: labels,
                    datasets: [{
                        label: value,
                        data: prices,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
                // clunky canvas cleanup to allow different stocks to load
                var oldcanv = document.getElementById('myChart');
                document.getElementById('chart').removeChild(oldcanv);
                var canv = document.createElement('canvas');
                canv.id = 'myChart';
                document.getElementById('chart').appendChild(canv);

                var ctx = document.getElementById('myChart').getContext('2d');
                var myLineChart = new Chart(ctx, {
                    type: 'line',
                    data: data2,
                    options: {
                        animations: {
                            tension: {
                                duration: 1000,
                                easing: 'linear',
                                from: 1,
                                to: 0,
                                loop: false
                            }
                        },
                        scales: {
                            y: {
                                suggestedMin: Math.min.apply(Math, prices) * 0.9,
                                suggestedMax: Math.max.apply(Math, prices) * 1.05
                            }
                        }
                    }
                });
            })
            .catch(err => {
                throw new Error("Symbol processing failed " + err);
            })
    }
})
