let notificadas = [];

function solicitarPermissao() {
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
}

function exibirNotificacao(tarefa) {
    if (!notificadas.includes(tarefa.hora)) {
        new Notification("Tarefa Agendada", {
            body: tarefa.description
        });
        notificadas.push(tarefa.hora);
    }
}

async function checarTarefas() {
    const res = await fetch('/tarefas');
    const tarefas = await res.json();

    const agora = new Date();
    const horaAtual = agora.toTimeString().slice(0, 5); // HH:MM

    tarefas.forEach(tarefa => {
        if (tarefa.hora === horaAtual && !tarefa.done) {
            exibirNotificacao(tarefa);
        }
    });

    atualizarLista(tarefas);
}


function atualizarLista(tarefas) {
    const ul = document.getElementById("lista-tarefas");
    ul.innerHTML = "";
    tarefas.forEach(tarefa => {
        const li = document.createElement("li");
        li.textContent = `${tarefa.hora} - ${tarefa.description}`;
        ul.appendChild(li);
    });
}

async function toggleTarefa(id) {
    // Envia POST para alternar status
    await fetch(`/toggle_agenda/${id}`, { method: 'POST' });
    // Atualiza lista depois de alterar
    checarTarefas();
}

function atualizarLista(tarefas) {
    const ul = document.getElementById("lista-tarefas");
    ul.innerHTML = "";

    tarefas.forEach(tarefa => {
        const li = document.createElement("li");
        if (tarefa.done) li.classList.add("inativa");

        const texto = document.createElement("span");
        texto.textContent = `${tarefa.hora} - ${tarefa.description}`;
        li.appendChild(texto);

        // Container de botões
        const botoes = document.createElement("div");
        botoes.classList.add("grupo-botoes");

        const btnToggle = document.createElement("button");
        btnToggle.textContent = tarefa.done ? "Ativar" : "Desativar";
        btnToggle.classList.add("btn-toggle");
        btnToggle.onclick = () => toggleTarefa(tarefa.id);
        botoes.appendChild(btnToggle);

        if (!tarefa.done) {
            const btnExcluir = document.createElement("button");
            btnExcluir.textContent = "Excluir";
            btnExcluir.classList.add("btn-excluir");
            btnExcluir.onclick = () => deleteTarefa(tarefa.id);
            botoes.appendChild(btnExcluir);
        }

        li.appendChild(botoes);
        ul.appendChild(li);
    });
}

async function deleteTarefa(id) {
    const confirmar = confirm("Tem certeza que deseja excluir esta tarefa?");
    if (!confirmar) return;

    try {
        await fetch(`/delete_agenda/${id}`, { method: 'POST' });
        checarTarefas(); // Atualiza a lista após excluir
    } catch (error) {
        console.error("Erro ao excluir tarefa:", error);
    }
}



solicitarPermissao();
checarTarefas();
setInterval(checarTarefas, 60000); // a cada 1 min
