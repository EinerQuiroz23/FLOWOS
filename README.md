# FlowOS

**FlowOS** is an intelligent platform designed to optimize software companies by smartly assigning projects, tasks, and teams based on skills, experience, and availability.

## Features

- Intelligent team and leader proposal (OPTIMA)
- Multi-organization support
- Role-based access (Super Admin, Admin, Secretary, Employee)
- Employee self-registration with organization code
- Password recovery via email (6-digit code)
- Skills, availability, and workload management

## Tech Stack

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication

### Frontend

- (React / Vite - pending documentation)

## Roles

| Role            | Description                                    |
| --------------- | ---------------------------------------------- |
| **Super Admin** | Creates organizations and their Admins         |
| **Admin**       | Full control of the organization + OPTIMA      |
| **Secretary**   | Operational management (people, basic data)    |
| **Employee**    | Views tasks, team, profile. Can be team leader |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tu-usuario/flowos.git
cd flowos
```
