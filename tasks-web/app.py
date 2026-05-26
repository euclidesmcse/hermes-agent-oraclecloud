import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Anakin & Tasks Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

# Task Model
class Task(BaseModel):
    id: str
    content: str
    category: str  # Anakin, Projetos, Compras, Geral
    date: Optional[str] = None
    time: Optional[str] = None
    status: str = "pending"  # pending, completed
    created_at: str

class TaskCreate(BaseModel):
    content: str
    category: Optional[str] = "Geral"
    date: Optional[str] = None
    time: Optional[str] = None

# Helper functions to read/write JSON
def read_tasks() -> List[dict]:
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def write_tasks(tasks: List[dict]):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.get("/api/tasks")
def get_tasks():
    return read_tasks()

@app.post("/api/tasks")
def create_task(task_in: TaskCreate):
    tasks = read_tasks()
    new_task = {
        "id": str(uuid.uuid4()),
        "content": task_in.content,
        "category": task_in.category or "Geral",
        "date": task_in.date,
        "time": task_in.time,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.insert(0, new_task)  # Prepend new tasks
    write_tasks(tasks)
    return new_task

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: str):
    tasks = read_tasks()
    found = False
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "completed"
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Task not found")
    write_tasks(tasks)
    return {"status": "success", "message": "Task marked as completed"}

@app.post("/api/tasks/{task_id}/pending")
def mark_pending(task_id: str):
    tasks = read_tasks()
    found = False
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "pending"
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Task not found")
    write_tasks(tasks)
    return {"status": "success", "message": "Task marked as pending"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    tasks = read_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    write_tasks(new_tasks)
    return {"status": "success", "message": "Task deleted"}

# Embed HTML Template directly for zero-dependencies and instant loading
@app.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Tarefas - Anakin & Co.</title>
        <!-- Tailwind CSS CDN -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- FontAwesome Icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            dark: {
                                900: '#0F172A', // slate 900
                                800: '#1E293B', // slate 800
                                700: '#334155', // slate 700
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
            }
            .checkbox-custom:checked + label {
                text-decoration: line-through;
                color: #94A3B8;
            }
            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 6px;
            }
            ::-webkit-scrollbar-track {
                background: #0F172A;
            }
            ::-webkit-scrollbar-thumb {
                background: #334155;
                border-radius: 3px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #475569;
            }
        </style>
    </head>
    <body class="bg-dark-900 text-slate-100 min-h-screen pb-12">

        <!-- Navigation Bar -->
        <nav class="border-b border-slate-800 bg-dark-800/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
            <div class="max-w-4xl mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="bg-indigo-600 p-2 rounded-lg text-white">
                        <i class="fa-solid fa-square-check text-xl"></i>
                    </div>
                    <div>
                        <h1 class="text-lg font-bold tracking-tight">Anakin & Tasks</h1>
                        <p class="text-xs text-slate-400">Painel de Lembretes & Tarefas</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <span id="connection-badge" class="flex items-center space-x-1.5 text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full font-medium">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span>Sincronizado</span>
                    </span>
                    <button onclick="fetchTasks()" class="text-slate-400 hover:text-white transition-colors p-1.5 hover:bg-slate-700/50 rounded-lg" title="Atualizar agora">
                        <i class="fa-solid fa-arrows-rotate"></i>
                    </button>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <main class="max-w-4xl mx-auto px-6 mt-8">
            
            <!-- Quick Stats & Anakin Section -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <!-- Anakin Status -->
                <div class="md:col-span-2 bg-gradient-to-r from-indigo-900/40 to-slate-800 p-5 rounded-xl border border-indigo-500/20 flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="bg-indigo-500/20 p-4 rounded-xl text-indigo-400 text-3xl">
                            <i class="fa-solid fa-dog"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-100">Anakin Skywalker 🐕</h3>
                            <p class="text-sm text-indigo-200">Seu cão de estimação e parceiro!</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-xs bg-indigo-500/20 text-indigo-300 font-semibold px-2.5 py-1 rounded-full">Ativo</span>
                    </div>
                </div>

                <!-- Active Tasks Count -->
                <div class="bg-dark-800 p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tarefas Ativas</p>
                        <h2 id="pending-count" class="text-3xl font-bold mt-1 text-slate-100">0</h2>
                    </div>
                    <div class="bg-indigo-500/10 p-3 rounded-lg text-indigo-400 text-2xl">
                        <i class="fa-solid fa-list-check"></i>
                    </div>
                </div>
            </div>

            <!-- Fast Quick-Add Form -->
            <div class="bg-dark-800 border border-slate-800 rounded-xl p-5 mb-8">
                <h3 class="text-sm font-semibold text-slate-300 mb-3"><i class="fa-solid fa-plus mr-2 text-indigo-400"></i>Nova Tarefa / Lembrete Rápido</h3>
                <form id="add-task-form" onsubmit="createTask(event)" class="space-y-3">
                    <div class="flex flex-col md:flex-row gap-3">
                        <input type="text" id="task-content" required placeholder="Ex: Dar banho no Anakin, Comprar pão, Terminar projeto X..." 
                            class="flex-grow bg-dark-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 transition-colors text-slate-100 placeholder-slate-500">
                        
                        <div class="flex gap-2">
                            <select id="task-category" class="bg-dark-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-slate-300">
                                <option value="Geral">📁 Geral</option>
                                <option value="Anakin">🐕 Anakin Care</option>
                                <option value="Projetos">💻 Projetos</option>
                                <option value="Compras">🛒 Compras</option>
                            </select>
                            
                            <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition-colors flex items-center space-x-1">
                                <i class="fa-solid fa-plus text-xs"></i> <span>Criar</span>
                            </button>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Filter Buttons -->
            <div class="flex flex-wrap gap-2 mb-6">
                <button onclick="setFilter('all')" id="filter-all" class="filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-indigo-600 text-white shadow-lg shadow-indigo-600/15">Todas</button>
                <button onclick="setFilter('Anakin')" id="filter-Anakin" class="filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-slate-800 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200">🐕 Anakin Care</button>
                <button onclick="setFilter('Projetos')" id="filter-Projetos" class="filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-slate-800 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200">💻 Projetos</button>
                <button onclick="setFilter('Compras')" id="filter-Compras" class="filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-slate-800 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200">🛒 Compras</button>
                <button onclick="setFilter('Geral')" id="filter-Geral" class="filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-slate-800 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200">📁 Geral</button>
            </div>

            <!-- Task List Section -->
            <div class="space-y-4">
                <h3 class="text-xs uppercase font-bold text-slate-500 tracking-wider mb-2">Tarefas Pendentes</h3>
                <div id="tasks-list-pending" class="space-y-2">
                    <!-- Dynamic Loading -->
                    <div class="text-center py-12 text-slate-500">
                        <i class="fa-solid fa-circle-notch animate-spin text-2xl mb-2 text-indigo-500"></i>
                        <p class="text-sm">Carregando tarefas...</p>
                    </div>
                </div>
            </div>

            <!-- Completed Section -->
            <div class="mt-10 border-t border-slate-800 pt-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xs uppercase font-bold text-slate-500 tracking-wider">Concluídas recentemente</h3>
                    <button onclick="toggleCompletedList()" id="toggle-completed-btn" class="text-xs font-semibold text-slate-400 hover:text-indigo-400 transition-colors">
                        Ocultar Concluídas
                    </button>
                </div>
                <div id="tasks-list-completed" class="space-y-2 opacity-60">
                    <!-- Dynamic Loading -->
                </div>
            </div>

        </main>

        <script>
            let allTasks = [];
            let currentFilter = 'all';
            let showCompleted = true;

            // Fetch tasks from API
            async function fetchTasks() {
                try {
                    const response = await fetch('/api/tasks');
                    allTasks = await response.json();
                    renderTasks();
                    updateBadge(true);
                } catch (error) {
                    console.error("Erro ao carregar tarefas:", error);
                    updateBadge(false);
                }
            }

            // Update Sincronizado badge status
            function updateBadge(success) {
                const badge = document.getElementById('connection-badge');
                if (success) {
                    badge.className = "flex items-center space-x-1.5 text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full font-medium";
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span>Sincronizado</span>`;
                } else {
                    badge.className = "flex items-center space-x-1.5 text-xs bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-full font-medium";
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-400"></span><span>Desconectado</span>`;
                }
            }

            // Toggle show completed tasks list
            function toggleCompletedList() {
                showCompleted = !showCompleted;
                const list = document.getElementById('tasks-list-completed');
                const btn = document.getElementById('toggle-completed-btn');
                if (showCompleted) {
                    list.classList.remove('hidden');
                    btn.textContent = "Ocultar Concluídas";
                } else {
                    list.classList.add('hidden');
                    btn.textContent = "Mostrar Concluídas";
                }
            }

            // Set category filters
            function setFilter(category) {
                currentFilter = category;
                
                // Update button styles
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.className = "filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-slate-800 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200";
                });
                
                const activeBtn = document.getElementById(`filter-${category}`);
                if (activeBtn) {
                    activeBtn.className = "filter-btn px-4 py-1.5 rounded-lg text-sm font-medium transition-all bg-indigo-600 text-white shadow-lg shadow-indigo-600/15";
                }
                
                renderTasks();
            }

            // Render task elements to screen
            function renderTasks() {
                const pendingContainer = document.getElementById('tasks-list-pending');
                const completedContainer = document.getElementById('tasks-list-completed');
                
                let filtered = allTasks;
                if (currentFilter !== 'all') {
                    filtered = allTasks.filter(t => t.category === currentFilter);
                }

                const pendingTasks = filtered.filter(t => t.status === 'pending');
                const completedTasks = filtered.filter(t => t.status === 'completed');

                // Update counter
                document.getElementById('pending-count').textContent = allTasks.filter(t => t.status === 'pending').length;

                // Pending List HTML
                if (pendingTasks.length === 0) {
                    pendingContainer.innerHTML = `
                        <div class="text-center py-10 bg-dark-800/40 rounded-xl border border-dashed border-slate-800 text-slate-500">
                            <i class="fa-solid fa-circle-check text-2xl mb-2 text-indigo-500/55"></i>
                            <p class="text-sm">Nenhuma tarefa pendente por aqui!</p>
                        </div>
                    `;
                } else {
                    pendingContainer.innerHTML = pendingTasks.map(t => getTaskRowHTML(t)).join('');
                }

                // Completed List HTML
                if (completedTasks.length === 0) {
                    completedContainer.innerHTML = `<p class="text-xs text-slate-500 text-center py-4">Nenhuma concluída recentemente.</p>`;
                } else {
                    completedContainer.innerHTML = completedTasks.slice(0, 15).map(t => getTaskRowHTML(t)).join('');
                }
            }

            // Get Category Badge Style
            function getCategoryBadge(cat) {
                switch(cat) {
                    case 'Anakin':
                        return `<span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/10">🐕 Anakin Care</span>`;
                    case 'Projetos':
                        return `<span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/10">💻 Projetos</span>`;
                    case 'Compras':
                        return `<span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/10">🛒 Compras</span>`;
                    default:
                        return `<span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-md bg-slate-500/10 text-slate-400 border border-slate-500/10">📁 Geral</span>`;
                }
            }

            // Generate HTML structure for task row
            function getTaskRowHTML(task) {
                const isCompleted = task.status === 'completed';
                const checkboxId = `task-${task.id}`;
                const badge = getCategoryBadge(task.category);
                
                // Show date/time if available
                let dateTimeHTML = '';
                if (task.date || task.time) {
                    const icon = task.time ? 'fa-regular fa-clock' : 'fa-regular fa-calendar';
                    const timeStr = task.time ? task.time : '';
                    const dateStr = task.date ? task.date : '';
                    const displayTime = [dateStr, timeStr].filter(Boolean).join(' às ');
                    dateTimeHTML = `
                        <span class="flex items-center space-x-1 text-xs text-indigo-300 font-medium bg-indigo-500/5 px-2 py-0.5 rounded border border-indigo-500/5">
                            <i class="${icon} text-[10px]"></i>
                            <span>${displayTime}</span>
                        </span>
                    `;
                }

                return `
                    <div id="row-${task.id}" class="flex items-center justify-between bg-dark-800 border ${isCompleted ? 'border-slate-800/50 bg-dark-800/50' : 'border-slate-800'} rounded-xl p-4 transition-all hover:border-slate-700">
                        <div class="flex items-center space-x-3.5 flex-grow mr-4">
                            <input type="checkbox" id="${checkboxId}" ${isCompleted ? 'checked' : ''} 
                                onclick="toggleTaskCompletion('${task.id}', ${isCompleted})"
                                class="checkbox-custom w-5 h-5 rounded-md text-indigo-600 bg-dark-900 border-slate-700 focus:ring-indigo-500 focus:ring-offset-dark-900 focus:ring-2 cursor-pointer transition-colors">
                            <div class="flex flex-col">
                                <label for="${checkboxId}" class="text-sm font-medium cursor-pointer ${isCompleted ? 'line-through text-slate-500' : 'text-slate-200'} select-none leading-relaxed break-all">
                                    ${task.content}
                                </label>
                                <div class="flex items-center gap-2 mt-1.5">
                                    ${badge}
                                    ${dateTimeHTML}
                                </div>
                            </div>
                        </div>
                        <button onclick="deleteTask('${task.id}')" class="text-slate-500 hover:text-rose-400 transition-colors p-1.5 hover:bg-rose-500/5 rounded-lg" title="Excluir">
                            <i class="fa-solid fa-trash-can text-sm"></i>
                        </button>
                    </div>
                `;
            }

            // Create new task
            async function createTask(e) {
                e.preventDefault();
                const contentInput = document.getElementById('task-content');
                const categorySelect = document.getElementById('task-category');
                
                const content = contentInput.value.trim();
                const category = categorySelect.value;
                
                if (!content) return;

                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content, category })
                    });
                    
                    if (response.ok) {
                        contentInput.value = '';
                        await fetchTasks();
                    }
                } catch (error) {
                    console.error("Erro ao criar tarefa:", error);
                }
            }

            // Toggle task state (completed <-> pending)
            async function toggleTaskCompletion(taskId, currentlyCompleted) {
                const endpoint = currentlyCompleted ? `/api/tasks/${taskId}/pending` : `/api/tasks/${taskId}/complete`;
                const row = document.getElementById(`row-${taskId}`);
                
                // Optimistic UI updates
                if (row) {
                    row.style.opacity = '0.4';
                }

                try {
                    const response = await fetch(endpoint, { method: 'POST' });
                    if (response.ok) {
                        await fetchTasks();
                    } else {
                        throw new Error("Failed update");
                    }
                } catch (error) {
                    console.error("Erro ao alternar status da tarefa:", error);
                    await fetchTasks(); // rollback
                }
            }

            // Delete a task
            async function deleteTask(taskId) {
                if (!confirm("Tem certeza que deseja excluir esta tarefa permanentemente?")) return;
                
                const row = document.getElementById(`row-${taskId}`);
                if (row) {
                    row.style.opacity = '0.3';
                }

                try {
                    const response = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
                    if (response.ok) {
                        await fetchTasks();
                    }
                } catch (error) {
                    console.error("Erro ao excluir tarefa:", error);
                    await fetchTasks();
                }
            }

            // Page Load Initialization
            document.addEventListener('DOMContentLoaded', () => {
                fetchTasks();
                
                // Dynamic Polling: fetch tasks in background every 30 seconds
                setInterval(fetchTasks, 30000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
