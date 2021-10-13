$(function() {
    $('#datetimepicker1').datetimepicker({ 
        format: 'YYYY-MM-DD',
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-chevron-up",
            down: "fa fa-chevron-down",
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'fa fa-screenshot',
            clear: 'fa fa-trash',
            close: 'fa fa-remove'
        }
    });
  });
  
  var formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'NGN',
  
    // These options are needed to round to whole numbers if that's what you want.
    //minimumFractionDigits: 0, // (this suffices for whole numbers, but will print 2500.10 as $2,500.1)
    //maximumFractionDigits: 0, // (causes 2500.99 to be printed as $2,501)
  });

$(document).ready(function() {
    
    let id = window.location.pathname
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    let settings = document.getElementById("settings");

    let dashboardImg = document.getElementById("dashboard-mobile-img");
    let invoiceImg = document.getElementById("invoice-mobile-img");
    let walletImg = document.getElementById("wallet-mobile-img");
    let statsImg = document.getElementById("stats-mobile-img");
    if (id ==="/invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");

        dashboardImg.src="/static/img/dashboard-mobile.svg"
        invoiceImg.src="/static/img/invoice-mobile.svg"
    }
    if (id ==="/dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id ==="/wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");

        dashboardImg.src="/static/img/dashboard-mobile.svg"
        walletImg.src="/static/img/wallet-mobile.svg"
    }
    if (id ==="/stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");

        dashboardImg.src="/static/img/dashboard-mobile.svg"
        statsImg.src="/static/img/stats-mobile.svg"
    }
    if (id ==="/settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        settings.classList.add("activ");
    }
   
   });
function makeActive(id) {
    console.log(id);
    let dashboard = document.getElementById("dashboard");
    let invoices = document.getElementById("invoices");
    let invoices2 = document.getElementById("invoices1");
    let settings = document.getElementById("settings");


    
    if (id === "invoices1" || id === "invoices"){
        invoices.classList.add("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="dashboard"){
        invoices.classList.remove("activ");
        dashboard.classList.add("activ");
        settings.classList.remove("activ");
    }
    if (id === "wallet1" || id ==="wallet"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id === "stats1" || id ==="stats"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
        settings.classList.remove("activ");
    }
    if (id ==="settings"){
        invoices.classList.remove("activ");
        dashboard.classList.remove("activ");
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
        let msg = document.getElementById("modal-message");
        let msgSuccess = document.getElementById("modal-message-success");

        let contBtnText = document.getElementById("WithBtnText");
        let contBtnImg = document.getElementById("withUploadImg");
        btn.disabled = false;
        contBtnText.innerText = "Withdrawal in Progress";
        contBtnImg.style.display = "inline-block";
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
                    msgSuccess.innerHTML = response.message; 
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
    })})

function in_checkFormOne() {
    let file= document.getElementById("file");
    let file_display= document.getElementById("file_display");
    if(file.value !== ""){
        file_display.value = file.value
    }
    
    let invoice_amount = document.getElementById("invoice_amount").value;
    let invoice = document.getElementById("invoice_name");
    let recieveable = document.getElementById("recieveable");
    let score = document.getElementById("score").value;
    let up_rec = document.getElementById("up_rec");
    let contBtn = document.getElementById("invoice_continue");
    if(invoice_amount !=""){
        recieveable.innerHTML= formatter.format(invoice_amount*(1-score));
        up_rec.classList.add("appear");
        up_rec.classList.remove("disappeared");
    }
    
    else if (file.value !== "" && invoice.value !== "" ){
        contBtn.disabled = false
        contBtn.classList.remove("btn-disabled");
        contBtn.classList.add("btn-create-account");
    }
    else{
        contBtn.disabled = true
        contBtn.classList.add("btn-disabled");
        contBtn.classList.remove("btn-create-account");
    }
}

function in_checkSelect(){
    
    let name= document.getElementById("vendor_name");
    let name2= document.getElementById("vendor_name2");
    if (name2.value === "new"){
        name.style.display = "block"
        name2.style.display = "none"
    }
}
function in_checkFormTwo() {
    let name= document.getElementById("vendor_name");
    let contact = document.getElementById("vendor_contact");
    let phone = document.getElementById("vendor_phone");
    let email = document.getElementById("vendor_email");
    
    let invoice_amount = document.getElementById("invoice_amount").value;
    let recieveable = document.getElementById("recieveable");
    let score = document.getElementById("score").value;
    let up_rec = document.getElementById("up_rec");
    if(invoice_amount !=""){
        recieveable.innerHTML= formatter.format(invoice_amount*(1-score));
        up_rec.classList.add("appear");
        up_rec.classList.remove("disappeared");
    }
    let contBtn = document.getElementById("in_btn-nxt");
    if (contact.value !== "" && phone.value !== "" && email.value !== ""){
        contBtn.disabled = false
        contBtn.classList.remove("btn-disabled");
        contBtn.classList.add("btn-create-account");
    }
    else{
        contBtn.disabled = true
        contBtn.classList.add("btn-disabled");
        contBtn.classList.remove("btn-create-account");
    }
}

$(function(){
    $('#invoice_continue').on('click', function (e) {
        e.preventDefault();
        let formOne = document.getElementById("up_form-inner-one");
        let formTwo = document.getElementById("up_form-inner-two");
        formOne.classList.add("disappeared");
        formOne.classList.remove("appear");
        formTwo.classList.add("appear");
        formTwo.classList.remove("disappeared");
})})
$(function(){
    $('#up_btn-back-one').on('click', function (e) {
        e.preventDefault();
        let formOne = document.getElementById("up_form-inner-one");
        let formTwo = document.getElementById("up_form-inner-two");
        formOne .classList.add("appear");
        formTwo.classList.add("disappeared");
        formTwo.classList.remove("appear");
})})

function searchInvoice() {
    $('#ajax_div').empty();
    $('#search-mobile').empty();
    let status = document.getElementById("select-filter").value 
    let status2 = document.getElementById("select-filter2").value;
    let date = document.getElementById("select-filter-date").value 
    let date2 = document.getElementById("select-filter-date2").value;
    console.log("date: ", date2)
    console.log("status: ", status2)
    let table = document.getElementById("invoice-table");
    let mobileTable = document.getElementById("mobile-table");
    let $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    if (status !="" || date !="0" && date !=""){
        table.style.display = "none";
        mobileTable.style.display = "none";

        let data={
            status: status,
            date: date,
        }
        console.log(data)
        $.ajax({
            url:'/invoice_search',
            type:'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            headers:{"X-CSRFToken": $crf_token},
            data:JSON.stringify(data),
            success:function(response){
                
                let invoiceList = response.invoices;
                console.log(invoiceList);
                if(invoiceList.length > 0){
                    invoiceList.forEach((element) => {
                        $('#ajax_div').append(
                                '<tr><td > <img src= "/static/img/invoice-small.svg" alt="upload" class="mr-1"/> '+element.additional_details.substring(0, 55)+'</td>'+
                                (element.invoice_state == 0 && '<td><span class="awaiting">Awaiting Confirmation</span></td>')+
                                (element.invoice_state == 1 && '<td><span class="vendor">Confirmed</span></td>')+
                                (element.invoice_state == 2 && '<td><span class="buyer">Awaiting Buyer</span></td>')+
                                (element.invoice_state == 3 && '<td><span class="maturity">Sold</span></td>')+
                                (element.invoice_state == 4 && '<td><span class="maturity">Completed</span></td>')+
                                '<td>'+formatter.format(element.invoice_amount)+'</td>'+
                                '<td>'+element.due_date+'</td>'+
                                '<td>'+element.vendor_name+'</td>'+
                                '<td><a href="'+element.invoice_url+'" target="_blank"><img src="/static/img/eye_hidden.svg" class="img-eye" /></a></td>'+
                                '</tr>'
                        );
                        $('#search-mobile').append(
                            '<div class="mobile-card-invoice mb-1" id="mobile-table">'+
                            '<div class="mob-flex">'+
                              '<h5>'+
                                '<img src= "/static/img/invoice-small.svg" alt="upload" class="mr-1"/>'+ 
                                element.additional_details.substring(0, 55)+
                            '</h5>'+
                              '<a href="'+element.invoice_url+'" target="_blank"><img src="/static/img/eye_hidden.svg" class="img-eye mt-3" style="width:70%;" /></a>'+
                            '</div>'+
                            
                            '<div class="mob-flex">'+
                                (element.invoice_state == 0 ? '<p class="awaiting">Awaiting Confirmation</p>': "")+
                                (element.invoice_state == 1 ? '<p class="vendor">Confirmed</p>' : "")+
                                (element.invoice_state == 2 ? '<p class="buyer">Awaiting Buyer</p>' :"")+
                                (element.invoice_state == 3 ? '<p class="maturity">Sold</p>' :"")+
                                (element.invoice_state == 4 ? '<td><span class="maturity">Completed</span></td>':"")+
                                '<p style="padding: 0.5rem;">'+formatter.format(element.invoice_amount)+'</p>'+
                            '</div>'+
                            '<div class="mob-flex">'+
                                '<p class="mob-p"> <img src= "/static/img/small-date.svg" alt="upload" class="mr-1"/>'+element.due_date+'</p>'+
                                '<p class="mob-p"> <img src= "/static/img/small-person.svg" alt="upload" class="mr-1"/>'+element.vendor_name+'</p>'+
                            '</div>'+
                            '</div>'
                        )
                    });
                }
                
                else{
                    $('#ajax_div').append(
                        '<tr>'+
                        '<td style="visibility:collapse;">'+
                        '<td style="visibility:collapse;">'+
                        
                        '<td style="text-align:center">'+
                            '<img src= "/static/img/no-invoice.svg" alt="upload" class="mb-3"/>'+
                            '<p>There are no Invoices due within '+date+' days from now </p>'+
                        '</td>'+
                        '<td style="visibility:collapse;">'+
                        '<td style="visibility:collapse;">'+
                        '</tr>'
                    );
                    $('#search-mobile').append(
                       '<div class="no-invoice">'+
                        '<img src= "/static/img/no-invoice.svg" alt="upload" class="mb-3"/>'+
                        '<p>No Invoices</p>'+
                      '</div>'
                    )
                }
            },
            error:function(e){
                console.log(e);
            },
        });
    }
    else if (status2 !="" || date2 !="0" && date2 !=""){
        table.style.display = "none";
        mobileTable.style.display = "none";

        let data={
            status: status2,
            date: date2,
        }
        console.log(data)
        $.ajax({
            url:'/invoice_search',
            type:'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            headers:{"X-CSRFToken": $crf_token},
            data:JSON.stringify(data),
            success:function(response){
                
                let invoiceList = response.invoices;
                console.log(invoiceList);
                if(invoiceList.length > 0){
                    invoiceList.forEach((element) => {
                        
                            $('#ajax_div').append(
                                '<tr><td > <img src= "/static/img/invoice-small.svg" alt="upload" class="mr-1"/> '+element.additional_details.substring(0, 55)+'</td>'+
                                (element.invoice_state == 0 && '<td><span class="awaiting">Awaiting Confirmation</span></td>')+
                                (element.invoice_state == 1 && '<td><span class="vendor">Confirmed</span></td>')+
                                (element.invoice_state == 2 && '<td><span class="buyer">Awaiting Buyer</span></td>')+
                                (element.invoice_state == 3 && '<td><span class="maturity">Sold</span></td>')+
                                (element.invoice_state == 4 && '<td><span class="maturity">Completed</span></td>')+
                                '<td>'+formatter.format(element.invoice_amount)+'</td>'+
                                '<td>'+element.due_date+'</td>'+
                                '<td>'+element.vendor_name+'</td>'+
                                '<td><a href="'+element.invoice_url+'" target="_blank"><img src="/static/img/eye_hidden.svg" class="img-eye" /></a></td>'+
                                '</tr>'
                            );
                     
                        
                        $('#search-mobile').append(
                            '<div class="mobile-card-invoice mb-1" id="mobile-table">'+
                            '<div class="mob-flex">'+
                              '<h5>'+
                                '<img src= "/static/img/invoice-small.svg" alt="upload" class="mr-1"/>'+ 
                                element.additional_details.substring(0, 55)+
                            '</h5>'+
                              '<a href="'+element.invoice_url+'" target="_blank"><img src="/static/img/eye_hidden.svg" class="img-eye mt-3" style="width:70%;" /></a>'+
                            '</div>'+
                            '<div class="mob-flex">'+
                            (element.invoice_state == 0 ? '<p class="awaiting">Awaiting Confirmation</p>': "")+
                            (element.invoice_state == 1 ? '<p class="vendor">Confirmed</p>' : "")+
                            (element.invoice_state == 2 ? '<p class="buyer">Awaiting Buyer</p>' :"")+
                            (element.invoice_state == 3 ? '<p class="maturity">Sold</p>' :"")+
                            (element.invoice_state == 4 ? '<td><span class="maturity">Completed</span></td>':"")+
                                '<p style="padding: 0.5rem;">'+formatter.format(element.invoice_amount)+'</p>'+
                            '</div>'+
                            '<div class="mob-flex">'+
                                '<p class="mob-p"> <img src= "/static/img/small-date.svg" alt="upload" class="mr-1"/>'+element.due_date+'</p>'+
                                '<p class="mob-p"> <img src= "/static/img/small-person.svg" alt="upload" class="mr-1"/>'+element.vendor_name+'</p>'+
                            '</div>'+
                            '</div>'
                        )
                    });
                }
                
                else{
                    $('#ajax_div').append(
                        '<tr>'+
                        '<td style="visibility:collapse;">'+
                        '<td style="visibility:collapse;">'+
                        
                        '<td style="text-align:center">'+
                            '<img src= "/static/img/no-invoice.svg" alt="upload" class="mb-3"/>'+
                            '<p>There are no Invoices due within '+date2+' days from now </p>'+
                        '</td>'+
                        '<td style="visibility:collapse;">'+
                        '<td style="visibility:collapse;">'+
                        '</tr>'
                    );
                    $('#search-mobile').append(
                       '<div class="no-invoice">'+
                        '<img src= "/static/img/no-invoice.svg" alt="upload" class="mb-3"/>'+
                        '<p>No Invoices</p>'+
                      '</div>'
                    )
                }
            },
            error:function(e){
                console.log(e);
            },
        });
    }
    else{
        table.style.display = "block";
        mobileTable.style.display = "block";
    }
}

function viewInvoice(id){
    console.log("Invoice ID:", id)
    let invoiceImg = document.getElementById("invoice-img");
    let $crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    let data={
        invoice_id: id,
    }
    $.ajax({
        url:'/invoice_details',
        type:'POST',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers:{"X-CSRFToken": $crf_token},
        data:JSON.stringify(data),
        success:function(response){
            console.log(response)
            invoiceImg.src = response.invoiceURL;
            $('#invoiceDetailsModal').modal('show');
            
        },
        error:function(e){
            console.log(e);
        },
    });
}

function changeBtn(){
    let contBtnText = document.getElementById("btnText");
    let contBtn = document.getElementById("in_btn-nxt");
    let contBtnImg = document.getElementById("uploadImg");
    contBtn.disabled = false;
    contBtnText.innerText = "Uploading";
    contBtnImg.style.display = "inline-block";
    contBtn.style.padding = "5px";
    console.log(contBtnImg.src)
}