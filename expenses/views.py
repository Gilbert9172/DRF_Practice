from rest_framework.generics import (
    ListCreateAPIView,RetrieveUpdateDestroyAPIView
)
from rest_framework import permissions
from .permissions import IsOwner
from .serializers import ExpenseSerializer,ExpensesSerializer
from .models import Expense

class ExpenseListAPIView(ListCreateAPIView):

    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    permission_class = (permissions.IsAuthenticated)

    #-- CreateModelMixin
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    #-- GenericAPIView
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
    

class ExpenseDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExpensesSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Expense.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)