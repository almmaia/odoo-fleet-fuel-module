# Odoo Fleet Fuel Control Module

Custom Odoo module for tracking fuel usage, costs and vehicle consumption within fleet management.

This module extends Odoo Fleet to provide structured fuel control, enabling companies to monitor expenses and improve operational visibility.

---

## 🚀 Overview

Fleet management systems often lack detailed control over fuel consumption and cost tracking.
This module integrates directly with Odoo Fleet to register fuel entries per vehicle and generate structured cost data.

Designed as a practical ERP customization project simulating real business requirements.

---

## 🧠 Features

* Fuel registration per vehicle
* Cost tracking by refill
* Integration with Odoo Fleet (`fleet.vehicle`)
* Custom model for fuel records
* Form and tree views
* Basic validation and structure
* Ready for further analytics integration

---

## 🏗 Architecture

```
Odoo Module
└── controle_combustivel
    ├── models
    ├── views
    ├── security
    └── manifest
```

### Main Model

Fuel control records linked to vehicles:

* vehicle_id
* date
* liters
* price
* total_cost

---

## 🛠 Tech Stack

* Python (Odoo framework)
* Odoo Community
* XML Views
* ORM models
* ERP customization

---

## 📂 Installation

1. Place module inside:

```
custom_addons/
```

2. Restart Odoo container/server

3. Update apps list

4. Install module:

```
Fuel Control
```

---

## 🎯 Purpose

This project demonstrates:

* ERP customization
* Odoo module structure
* ORM modeling
* business logic implementation
* real-world system extension

Built as part of backend learning and real scenario simulation.

---

## 👨‍💻 Author

Alan Maia
Backend Developer
Brazil
