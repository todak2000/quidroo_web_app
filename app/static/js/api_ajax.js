
$(document).ready(function() {
    let id = window.location.pathname
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    // let wallet = document.getElementById("wallet");
    // let stats = document.getElementById("stats");
    let settings = document.getElementById("settings");
    if (id ==="/invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.add("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.add("activ");
    }
   
    // executes when HTML-Document is loaded and DOM is ready
    // alert("document is ready");
   });
function makeActive(id) {
    console.log(id);
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    // let wallet = document.getElementById("wallet");
    // let stats = document.getElementById("stats");
    let settings = document.getElementById("settings");
    if (id ==="invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.add("activ");
        // stats.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id ==="settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        // wallet.classList.remove("activ");
        // stats.classList.remove("activ");
        settings.classList.add("activ");
    }
    
    
}

function d_toggleBalance(id) {
    let qut = document.getElementById("d_qut");
    let fiat = document.getElementById("d_fiat");
    if (id === "d_qut") {
      qut.classList.add("hide");
      qut.classList.remove("shows");
      fiat.classList.add("shows");
      fiat.classList.remove("hide");
    } else {
      qut.classList.remove("hide");
      qut.classList.add("shows");
      fiat.classList.remove("shows");
      fiat.classList.add("hide");
      
    }
}
function w_toggleBalance(id) {
    let qut = document.getElementById("w_qut");
    let fiat = document.getElementById("w_fiat");
    if (id === "w_qut") {
      qut.classList.add("hide");
      qut.classList.remove("shows");
      fiat.classList.add("shows");
      fiat.classList.remove("hide");
    } else {
      qut.classList.remove("hide");
      qut.classList.add("shows");
      fiat.classList.remove("shows");
      fiat.classList.add("hide");
      
    }
}
function d_showBalance() {
    let balance_div= document.getElementById("balance_div");
    let d_not= document.getElementById("d_not");
    let showIcon = document.getElementById("d_show");
    let hideIcon = document.getElementById("d_hide");
    if (balance_div.style.display == "block") {
        balance_div.style.display = "none";
        d_not.style.display = "block";
        hideIcon.style.display = "block";
        showIcon.style.display = "none";
    } else {
        balance_div.style.display = "block";
      hideIcon.style.display = "none";
      d_not.style.display = "none";
      showIcon.style.display = "block";

      
    }
}
function w_showBalance() {
    let balance_div= document.getElementById("w_balance_div");
    let d_not= document.getElementById("w_not");
    let showIcon = document.getElementById("w_show");
    let hideIcon = document.getElementById("w_hide");
    if (balance_div.style.display == "block") {
        balance_div.style.display = "none";
        d_not.style.display = "block";
        hideIcon.style.display = "block";
        showIcon.style.display = "none";
    } else {
        balance_div.style.display = "block";
      hideIcon.style.display = "none";
      d_not.style.display = "none";
      showIcon.style.display = "block";

      
    }
}

// WITHDRAW API
$(function(){
    $('#withdraw-btn').on('click', function (e) {
        e.preventDefault();
        let amount = document.getElementById("amount").value;
        let $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
        let success = document.getElementById("success");
        let fail = document.getElementById("fail");
        let main =  document.getElementById("main-form");
        let hash = document.getElementById('hash');
        let btn = document.getElementById('withdraw-btn');
        let ref_url = document.getElementById('ref_url');
        let msg = document.getElementById("modal-message") || document.getElementById("modal-message-success");
        btn.innerHTML = "Initiating Transaction..."
        // let code = document.getElementById("code_verify").value;
        // document.getElementById("spinner").style.display = "block";
        $.ajax({
            url:'/withdraw',
            type:'POST',
            headers:{"X-CSRFToken": $crf_token},
            data:{
                amount: amount,
            },
            success:function(response){
                console.log(response)
                if(response.success == true && response.status == 200){
                    success.classList.remove("modal-hide");
                    success.classList.remove("modal-show");
                    main.classList.add("modal-hide");
                    hash.value = response.tx_hash;
                    msg.innerHTML = response.message; 
                    ref_url.href ="https://horizon-testnet.stellar.org/transactions/"+response.tx_hash+"/operations"
                }
                else{
                    fail.classList.remove("modal-hide");
                    fail.classList.remove("modal-show");
                    main.classList.add("modal-hide");
                    msg.innerHTML = response.message;
                }
            },
            error:function(e){
                console.log(e);
                $("#spinner").hide();
            },
        });
        
        
    });
});

$(function(){
    $('.close').on('click', function (e) {
        e.preventDefault();
        location.reload();  
    })
})
// FUND API
$(function(){
    $('#topup-btn').on('click', function (e) {
        e.preventDefault();
        let amount = document.getElementById("f_amount").value;
        let $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
        let success = document.getElementById("t_success");
        let fail = document.getElementById("t_fail");
        let main =  document.getElementById("t_main-form");
        let hash = document.getElementById('t_hash');
        let btn = document.getElementById('topup-btn');
        let ref_url = document.getElementById('ref_url_fund');
        let msg = document.getElementById("t_modal-message") || document.getElementById("t_modal-message-success");
        // document.getElementById("spinner").style.display = "block";
        btn.innerHTML = "Initiating Transaction..."
        $.ajax({
            url:'/topup',
            type:'POST',
            headers:{"X-CSRFToken": $crf_token},
            data:{
                amount: amount,
            },
            success:function(response){
                console.log(response)
                if(response.success == true && response.status == 200){
                    success.classList.remove("modal-hide");
                    success.classList.remove("modal-show");
                    main.classList.add("modal-hide");
                    hash.value = response.tx_hash;
                    msg.innerHTML = response.message; 
                    ref_url.href ="https://horizon-testnet.stellar.org/transactions/"+response.tx_hash+"/operations"
                }
                else{
                    fail.classList.remove("modal-hide");
                    fail.classList.remove("modal-show");
                    main.classList.add("modal-hide");
                    msg.innerHTML = response.message;
                }
            },
            error:function(e){
                console.log(e);
            },
        });
        
        
    });
});

//DROP DOWN
$(function(){
    $('#drop-down').on('click', function () {
        console.log("hi")
        let ul = document.getElementById("drop-list")
        if (ul.style.display === "none") {
            ul.style.display = "block";
          } else {
            ul.style.display = "none";
          }
        // if(ul.classList = "hide"){
        //     ul.classList.remove("hide");
        //     ul.classList.add("show");
        // }
        // else if (ul.classList = "show"){
        //     ul.classList.remove("show");
        //     ul.classList.add("hide");
        // }
        // else{}
    })})