
$(document).ready(function() {
    let id = window.location.pathname
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    let wallet = document.getElementById("wallet");
    let stats = document.getElementById("stats");
    let settings = document.getElementById("settings");
    if (id ==="/invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.add("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.add("activ");
    }
   
    // executes when HTML-Document is loaded and DOM is ready
    // alert("document is ready");
   });
function makeActive(id) {
    console.log(id);
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    let wallet = document.getElementById("wallet");
    let stats = document.getElementById("stats");
    let settings = document.getElementById("settings");
    if (id ==="invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.add("activ");
        stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id ==="settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        wallet.classList.remove("activ");
        stats.classList.remove("activ");
        settings.classList.add("activ");
    }
    
    
}