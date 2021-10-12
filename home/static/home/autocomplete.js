function autocomplete(user_input, tickers) {
    /* This is the autocomplete function takes two arguments: 
    1. user_input: user input parameters
    2. tickers : The list of stock tickers of possible autocompleted vaules */

    let currentFocus;

    /*execute a function when a user writes texts in the text field:*/
    user_input.addEventListener("input", function(e) {
        let div_1st, div_2nd, input_value = this.value;

        /*close any already open lists of autocompleted tickers*/
        closeAllLists();
        if (!input_value) {return false;}
        currentFocus = 0;

        /*create the first DIV element that will contain the items (values):
        and append the first DIV element as a child of the autocomplete container*/
        div_1st = document.createElement("DIV");
        div_1st.setAttribute("id", this.id + "autocomplete-list");
        div_1st.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(div_1st);

        /*for each ticker in tickers */
        for (let i = 0; i < tickers.length -1; i++) {

            /*check if the ticker include the letters that user wrote in the text field*/
            if (tickers[i].toUpperCase().includes(input_value.toUpperCase())) {

            /*create the second DIV element for each matching element
            Then, slice the name of the ticker(bold) and information parts in the ticker */
            div_2nd = document.createElement("DIV");
            let ticker_end = tickers[i].indexOf(',')
            let company_end = tickers[i].lastIndexOf(',')
            div_2nd.innerHTML = "<strong>" + tickers[i].substr(0, ticker_end) + "</strong>";
            div_2nd.innerHTML += "   "+ tickers[i].substr(ticker_end + 1, );
            div_2nd.innerHTML += "<input type='hidden' value='" + tickers[i] + "'>";

            /*execute a function that print the ticker name on the textfield 
            when the user clicks on the ticker value (DIV element):*/
            div_2nd.setAttribute("onclick", "location.href='" + `/agora/ticker/${tickers[i].substr(0, ticker_end)}` + "'");
            // div_2nd.addEventListener("click", function(e) {

            //     user_input.value = this.getElementsByTagName("input")[0].value.substr(0, ticker_end);
            //     closeAllLists();
            // });

            div_1st.appendChild(div_2nd);
            }
        }
        });
    
    /*execute a function presses a key on the keyboard:*/
    user_input.addEventListener("keydown", function(e) {
    let x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable
        and make the current item more visible:*/
        currentFocus++;
        addActive(x);
    } else if (e.keyCode == 38) { 
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable
        and make the current item more visible:*/
        currentFocus--;
        addActive(x);
    } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, 
        prevent the form from being submitted,
        and simulate a click on the "active" item*/
        e.preventDefault();
        if (currentFocus > -1) {
            if (x) x[currentFocus].click();
        }
    }
});

function addActive(x) {
    /*This is the function that classifies a ticker as "active":*/

    /*return false if is not excuted*/
    if (!x) return false;

    /*remove "active" class on all tickers before start*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
}

function removeActive(x) {
    /*This is the function removes the "active" class from all autocomplete tickers*/
    for (let i = 0; i < x.length; i++) {
    x[i].classList.remove("autocomplete-active");
    }
}

function closeAllLists(element) {
    /*close all autocomplete tickers in the document,
    except the one passed:*/
    let x = document.getElementsByClassName("autocomplete-items");
    for (let i = 0; i < x.length; i++) {
        if (element != x[i] && element != user_input) {
            x[i].parentNode.removeChild(x[i]);
        }
    }
}

/*execute a function when the user clicks a ticker in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});

}