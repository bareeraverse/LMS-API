# 📚 Learning Management System (LMS) API

A complete **RESTful API** for managing courses, students, teachers, and learning activities.  
Built with **Django REST Framework (DRF)**, this project covers authentication, course content, enrollments, quizzes, progress tracking, certificates, notifications, and reviews.

---

## 🚀 Features

1. **Authentication & User Management**
   - User registration & JWT authentication
   - Role-based access (Admin, Teacher, Student)
   - Profile management

2. **Course Management**
   - Create, update, delete, and list courses
   - Role restrictions (Teachers/Admin only can create)

3. **Modules & Lessons**
   - Organize courses into modules & lessons
   - CRUD operations for modules & lessons

4. **Enrollments**
   - Students can enroll/unenroll in courses
   - View enrolled courses

5. **Quizzes & Assessments**
   - Create quizzes per lesson
   - Submit answers and view results

6. **Progress Tracking**
   - Track student progress across courses

7. **Certificates**
   - Generate and view course completion certificates

8. **Notifications**
   - Admin/Teacher can send notifications
   - Students can view their notifications

9. **Reviews & Ratings**
   - Students can rate and review courses
   - Update or delete reviews

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework  
- **Auth**: JWT (djangorestframework-simplejwt)  
- **Database**: SQLite (default, can switch to PostgreSQL/MySQL)  
- **Tools**: Postman for API testing  

---
