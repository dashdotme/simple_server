// I've completely forgotten why, but this fixes the order of printing for the table
// let t2 = document.getElementById("access") 
// big ugly mess because understanding promise chaining took me a while
function loadStockTable(){

    fetch('portfolio.json')
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error: "+response.status);
            }
            return response.json();
        })
        .then(json => {
            var table = document.getElementById('access');
            json.portfolio.forEach(stock => {
                let url = `https://cloud.iexapis.com/stable/stock/${stock.symbol}/quote?token=${tk}`
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("HTTP error " + response.status);
                        }
                        return response.json();
                    })
                    .then(quote => {
                        var tr = document.createElement('tr');
                        var p = quote.latestPrice;
                        var s = stock.purchasePrice;
                        var v = ((p - s) / p * 100).toFixed(2);
                        // if (v < 0) v = `-\$${abs(val)}`; // require another .then layer to make this work
                        tr.innerHTML = '<td>' + stock.symbol + '</td>' +
                        '<td>' + stock.quantity + '</td>' +
                        '<td>' + stock.purchasePrice + '</td>' +
                        '<td>' + v + '</td>'
                        // '<td>' + parse(((p - s) / p * 100).toFixed(2)) + '</td>';
                        // '<td>' + round((p - s) / p * 100, 2) + '</td>';
                        table.appendChild(tr);
                    })
                    .catch(err => {
                        throw new Error("Parsing json failed.");
                    })
            })
        })
}

loadStockTable();


window.addEventListener('load', function () {
    const form = document.getElementById('theform');
    form.onreset = function() {
        fetch('reset', {
            method: 'POST',
            body: 'reset'
        })
        .then( arg => {
            setTimeout(location.reload(), 8000)
        })
}
})