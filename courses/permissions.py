from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "teacher"]
        )

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == "admin"
        )
    
class IsCourseTeacherOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        course = None
        if hasattr(obj,'course'):
            course = obj.course

        elif  hasattr(obj, 'module'):
            course= obj.module.course

        return bool(course and request.user == getattr(course,'teacher',None))