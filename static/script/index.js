let toastElement = document.querySelector('.toastElement');

if(toastElement){
    toastElement.classList.add('show');
    setTimeout(function() {
        toastElement.classList.remove('show');
    }, 2500);
}

function togglePassword (input_class, clas_show, clas_hide){
    let eye_show = document.querySelector(`.${clas_show}`)
    let eye_hide = document.querySelector(`.${clas_hide}`)
    let input = document.querySelector(`.${input_class}`)

    if(input.type == 'password'){
        input.type = 'text'
    }else{
        input.type = 'password'
    }

    eye_show.classList.toggle('hide')
    eye_hide.classList.toggle('hide')

    return
}




