# Weston Robot AE Evaluation Project – Minimal Mobile Robot Autonomy (ROS2 Humble + Nav2 + BT)

A minimal (yet realistic) software-centric mobile robot autonomy system for patrolling in a known 2D environment.
It integrates:
- A lightweight 2D kinematics simulator (odom/tf/cmd_vel + lidar ray casting)
- Nav2 for planning & navigation execution
- Application-level mission behavior using Behavior Trees (custom + Nav2 nodes)
- Safety gating & failure injection for robustness testing

> Focus: software architecture, robustness under failures, and reproducibility.

---

## 1. Requirements Coverage (Traceability)

This repository is built to satisfy the evaluation requirements:
- **Simulator**: publishes `/odom` + TF, consumes `/cmd_vel`, provides static map + obstacle representation, publishes sensor data usable by Nav2 (e.g. `/scan`)  
- **Nav2 integration**: global/local planning + execution, perfect/mildly noisy localization  
- **BT application behavior**: mission logic (loop patrol), progress monitoring, recovery escalation, safety gating, plus at least one configurable failure injection
- **Demos**: (1) normal mission execution (2) persistent obstacle / blocked path

---

## 2. Repository Structure

