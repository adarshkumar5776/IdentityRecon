# 🚀 Bitespeed Identity Reconciliation API

This Django-based **Identity Reconciliation API** helps **track and merge customer contacts** based on **email** and **phone number**. It ensures that a single customer has a **primary contact**, while all other linked contacts are marked as **secondary**.

---

## 📌 Features
- ✅ **Identifies and tracks customer contacts** across multiple orders.
- ✅ **Merges duplicate contacts** based on email and phone.
- ✅ **Ensures oldest contact remains primary**, converting others to secondary.
- ✅ **Built using Django REST Framework (DRF)** for easy integration.

---

## 🔧 Installation & Setup

### 1️ **Clone the Repository**
```
git clone https://github.com/adarshkumar5776/IdentityRecon.git
cd IdentityRecon
```

### 2 **Set Up a Virtual Environment**
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3 **Install Dependencies**
```
pip install -r requirements.txt
```

### 4 **Run Database Migrations**
```
python manage.py makemigrations contacts
python manage.py migrate
```

### 5 **Start the Django Server**
```
python manage.py runserver
```

### The API will be accessible at http://127.0.0.1:8000/


## 🚀 API Endpoints

### 🔹 `POST /identify`
This endpoint **identifies and consolidates customer contacts** based on email and phone number.

---

### **📌 Request Format**
The request must be a **JSON payload** containing at least an `email` or `phoneNumber`.

    ```
    {
      "email": "mcfly@hillvalley.edu",
      "phoneNumber": "123456"
    }

### **📌 Response Format**
The API returns a **JSON response** containing the consolidated contact information.

    ```
    {
      "contact": {
        "primaryContatctId": 1,
        "emails": ["lorraine@hillvalley.edu", "mcfly@hillvalley.edu"],
        "phoneNumbers": ["123456"],
        "secondaryContactIds": [23]
      }
    }

## 📌 How It Works

The **Identity Reconciliation API** works by consolidating customer contacts based on **email and phone number**.  
It follows these steps:

1. **If a contact with the given email or phone exists**:
   - Retrieves all related contacts linked by `email` or `phoneNumber`.
   - Identifies the **oldest primary contact**.
   - Converts all newer primary contacts into **secondary** contacts.
   - Ensures all contacts are correctly linked.

2. **If a new contact is provided**:
   - If it matches an existing contact, it **links to the primary**.
   - If no matches are found, it **creates a new primary contact**.

3. **If additional information (new email/phone) is found**:
   - A **secondary contact is created** and linked to the primary.

## 🌍 Hosted API Endpoint
The API is live at:  
🔗 **[https://assesment-new.onrender.com/identify](https://assesment-new.onrender.com/identify)**  

You can send a **POST request** to this endpoint using **cURL**:
```
    curl --location 'https://assesment-new.onrender.com/identify' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "email": "lorraine@hillvalley.edu",
        "phoneNumber": "123456"
    }'
```

## 📌 Database Schema (`Contact` Model)

The **Contact model** is responsible for storing customer contact details.  
Each contact is categorized as either **primary** (first occurrence) or **secondary** (linked to a primary contact).

```python
class Contact(models.Model):
    phoneNumber = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linkedId = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    linkPrecedence = models.CharField(
        max_length=10, 
        choices=[('primary', 'primary'), ('secondary', 'secondary')]
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deletedAt = models.DateTimeField(null=True, blank=True)


