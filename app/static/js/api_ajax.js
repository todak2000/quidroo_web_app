// SIGN UP API
$(function(){
    $('.btn-create-accounta').on('click', function (e) {
        e.preventDefault();
        let submit_btn = this.id
        console.log("user_role: ", submit_btn);
        if(submit_btn === "s_btn-nxt"){
            let business_type = document.getElementById("s_business_type").value;
            let company = document.getElementById("s_company").value;
            let email = document.getElementById("s_email").value;
            let cac = document.getElementById("s_cac").value;
            let password = document.getElementById("s_password").value;
            let address = document.getElementById("s_address").value;
            let role = "seller";

            let data={
                business_type: business_type,
                company_name: company,
                email: email,
                cac_no: cac,
                password: password,
                company_address: address,
                role: role,
            }
            $.ajax({
                url:'/signup',
                type:'POST',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                data:JSON.stringify(data),
                success:function(response){
                    // console.log(response)
                    if(response.success == false){
                        window.location.href = '/verify/'+response.user_id;
                        document.getElementById('server_message_error').classList.add("alert-danger");
                        document.getElementById('server_message_error').innerHTML = response.message;
                        document.getElementById("server_message_error").style.display = "block";
                        setTimeout(function(){ 
                            document.getElementById("server_message_error").style.display = "none";   
                        }, 3000);
                        
                    }
                    else{
                        window.location.href = '/verify/'+response.user_id;
                    }
                    console.log(response);
                },
                error:function(e){
                    console.log(e);
                    $("#spinner").hide();
                },
            });
        }

        // let firstname = document.getElementById("firstname").value;
        // let lastname = document.getElementById("lastname").value;
        // let email = document.getElementById("email").value;
        // let phonenumber = document.getElementById("phonenumber").value;
        // let password = document.getElementById("password").value;
        // let service = null;
        // let address = document.getElementById("address").value;
        // let role = document.getElementById("role").value;
        // if (role =="service_provider"){
        //     enumRole = 0;
        //     service = document.getElementById("sp_jobs").value;
        // }
        // else{ enumRole = 1}

        // let terms_conditions = document.getElementById("terms_conditions");
        // let state = document.getElementById("state").value;
        
        // let data={
        //     firstName: firstname,
        //     lastName: lastname,
        //     email: email,
        //     phoneNumber: phonenumber,
        //     password: password,
        //     address: address,
        //     role: enumRole,
        //     state: state,
        //     service: service
        // }
        // document.getElementById("spinner").style.display = "block";
        // if (terms_conditions.checked == false){
        //     document.getElementById("spinner").style.display = "none";
        //     document.getElementById('server_message_error').classList.add("alert-danger");
        //     document.getElementById('server_message_error').innerHTML = "Sorry! you need to agree to the Terms and Conditions to proceed.";
        //     document.getElementById("server_message_error").style.display = "block";
        //     setTimeout(function(){ 
        //         document.getElementById("server_message_error").style.display = "none"; 
        //     }, 3000);
        // }
        
        // else{
        //     $.ajax({
        //         url:base_url+'/signup',
        //         type:'POST',
        //         contentType: "application/json; charset=utf-8",
        //         dataType: "json",
        //         data:JSON.stringify(data),
        //         success:function(response){
        //             console.log(response)
        //             document.getElementById("spinner").style.display = "none";
        //             if(response.success == false){
        //                 document.getElementById('server_message_error').classList.add("alert-danger");
        //                 document.getElementById('server_message_error').innerHTML = response.message;
        //                 document.getElementById("server_message_error").style.display = "block";
        //                 setTimeout(function(){ 
        //                     document.getElementById("server_message_error").style.display = "none";   
        //                 }, 3000);
                        
        //             }
        //             else{
        //                 window.location.href = '/verify/'+response.user_id;
        //             }
        //             console.log(response);
        //         },
        //         error:function(e){
        //             console.log(e);
        //             $("#spinner").hide();
        //         },
        //     });
        // }
    });
});