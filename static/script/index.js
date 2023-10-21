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

async function openModalGroup(group_id){
    try {
        let resp = await fetch(`/modal_group/${group_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })

        resp = await resp.json()

        let modal = document.getElementById("modal_group")
        let content = document.getElementById("modal_content")
        content.innerHTML = ''

        let title = document.createElement("h5")
        title.innerHTML = resp.name

        let date = document.createElement("p")
        date.innerHTML = `Draw date: <span>${resp.draw_date}</span>`

        let ul = document.createElement("ul")
        resp.participants.forEach((member) => {
            let li = document.createElement("li")
            li.innerHTML = `<span>${member.name}</span> <span>${member.email}</span>`
            ul.append(li)
        })

        content.append(title, ul, date)
        modal.classList.remove("hide")


        console.log("Dados grupo", resp)
    } catch (error) {
        console.error("Error openModalGroup", error)
    }
}

function modalOutClick(event, ele_id){
    console.log("target", event.target)
    if(event.target.id == ele_id){
        event.target.classList.add("hide")
    }
}