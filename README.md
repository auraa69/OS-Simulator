# 🖥️ OS Simulator

An interactive **Operating System Simulator** built with Python and Streamlit. This project demonstrates three fundamental Operating System concepts through interactive simulations, visualizations, and real-time calculations.

🌐 **Live Demo:** https://os-simulator-bysibgatullah.streamlit.app/

## 🚀 Project Overview

The OS Simulator provides an interactive environment to understand and visualize how operating systems manage CPU scheduling, memory allocation, and resource management.

It includes three major modules:

1. CPU Scheduling Algorithms
2. Page Replacement Algorithms
3. Banker's Algorithm (Deadlock Avoidance)

## ✨ Features

### 1. CPU Scheduling

Simulates and compares three CPU scheduling algorithms:

- **FCFS (First Come First Serve)**
- **SJF (Shortest Job First)** – Non-preemptive
- **Round Robin**

**Features:**
- Custom process arrival and burst times
- Adjustable Round Robin time quantum
- Interactive Gantt chart visualization
- Animated Gantt chart with adjustable speed
- Average waiting time calculation
- Average turnaround time calculation
- Context switch calculation
- Compare all scheduling algorithms

### 2. Page Replacement

Simulates three popular page replacement algorithms:

- **FIFO (First In First Out)**
- **LRU (Least Recently Used)**
- **Optimal Page Replacement**

**Features:**
- Custom page reference string
- Adjustable number of memory frames
- Frame-by-frame simulation
- Page HIT and PAGE FAULT identification
- Total page faults and hits calculation
- Hit ratio calculation
- Visual comparison of all algorithms

### 3. Banker's Algorithm

Implements the Banker's Algorithm for deadlock avoidance.

**Features:**
- Custom number of processes
- Custom number of resource types
- Editable Allocation matrix
- Editable Maximum resource matrix
- Available resource configuration
- Automatic Need matrix calculation
- System safety checking
- Safe sequence detection
- Resource request validation
- Grant or deny resource requests based on system safety

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Matplotlib | Gantt chart visualization |
| Pandas | Data management and tables |

## 📂 Project Structure

```text
OS-Simulator/
│
├── .streamlit/
│   └── config.toml
│
├── os_sim.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

To run this project locally, follow these steps.

**1. Clone the repository**

```bash
git clone https://github.com/auraa69/OS-Simulator.git
```

**2. Navigate to the project directory**

```bash
cd OS-Simulator
```

**3. Install the required dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the application**

```bash
streamlit run os_sim.py
```

**5. Open the application**

Visit:

http://localhost:8501

## 🌍 Online Deployment

This application is deployed using **Streamlit Community Cloud**.

You can access the live application here:

👉 https://os-simulator-bysibgatullah.streamlit.app/

No local installation is required to use the online version.

## 🎯 Project Objectives

- Understand fundamental Operating System concepts.
- Visualize CPU scheduling techniques.
- Analyze memory management and page replacement strategies.
- Understand deadlock avoidance using Banker's Algorithm.
- Compare algorithm performance through interactive simulations.

## 👨‍💻 Developer

**auraa69**

GitHub: https://github.com/auraa69

Project: [OS Simulator](https://github.com/auraa69/OS-Simulator)

---

⭐ If you find this project useful, consider giving the repository a star!

**Built with Python and Streamlit.**
