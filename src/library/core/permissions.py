from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allows read-only access (GET, HEAD, OPTIONS) to anyone,
    but write operations (POST, PUT, PATCH, DELETE) only to staff users.
    """

    def has_permission(self, request, view):
        # Read-only methods are always allowed
        if request.method in SAFE_METHODS:
            return True
        # Write methods require staff
        return request.user and request.user.is_staff


class IsBorrowerOrAdmin(BasePermission):
    """
    For actions on a Loan object:
    - Only the borrower (the user who created the loan) or admin can perform actions like return.
    - This assumes the view has access to the Loan object (via get_object()).
    """

    def has_object_permission(self, request, view, obj):
        # Read is usually allowed if authenticated (handled by global)
        if request.method in SAFE_METHODS:
            return True

        # Write/return: only the borrower or staff
        return request.user == obj.user or request.user.is_staff


class IsBorrowerOrAdminForLoan(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.user or request.user.is_staff
