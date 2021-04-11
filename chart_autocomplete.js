// this is a (horrendous) duplication to fix a bug where autocomplete would prevent form submission,
// meaning that no chart could be retrieved

const symbols = [];
const tk = "pk_2502efcdd63f4ac1aa76ecf413ea4e65";

function populateSymbols() {
    // if (symbols.length > 100) {
    //     return
    // }
    let url = `https://cloud.iexapis.com/stable/ref-data/symbols?token=${tk}`
    fetch(url)
    .then (response => {
        if (!response.ok) {
            throw new Error("HTTP error "+response.status);
        } return response.json();
    })
    .then (val => {
        val.forEach((entry) => {
            if (entry.type == 'cs') symbols.push(entry.symbol);
        });
    })
    .catch(err => {
        throw new Error("Symbol processing failed "+err);
    })
}


// Autocomplete courtesy of https://www.w3schools.com/howto/howto_js_autocomplete.asp
// Not my own work & I take no credit! All I did was build the options array it uses

function autocomplete(textfield, optionsArr) {
    var currentFocus;

    textfield.addEventListener("input", function (e) {
        var a, b, i, val = this.value;

        closeAllLists();
        if (!val) { return false; }
        currentFocus = -1;

        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");

        this.parentNode.appendChild(a);

        for (i = 0; i < optionsArr.length; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (optionsArr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + optionsArr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += optionsArr[i].substr(val.length);
                /*insert a input field that will hold the current optionsArray item's value:*/
                b.innerHTML += "<input type='hidden' value='" + optionsArr[i] + "'>";
                b.addEventListener("click", function (e) {
                    textfield.value = this.getElementsByTagName("input")[0].value;

                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    textfield.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) { 
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != textfield) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}

populateSymbols();
window.addEventListener('load', function() {
    autocomplete(document.getElementById("symbol_input"), symbols);
})
