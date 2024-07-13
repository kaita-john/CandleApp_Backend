from datetime import timezone

import pandas as pd
from _decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academic_year.models import AcademicYear
from appcollections.models import Collection
from classes.models import Classes
from currencies.models import Currency
from file_upload.models import SchoolImage
from financial_years.models import FinancialYear
from invoices.models import Invoice
from invoices.views import createInvoices
from payment_in_kind_Receipt.models import PIKReceipt
from receipts.models import Receipt
from schoolgroups.models import SchoolGroup
from term.models import Term
from utils import SchoolIdMixin, UUID_from_PrimaryKey, currentAcademicYear, currentTerm, IsAdminOrSuperUser, \
    generate_unique_code, DefaultMixin
from voteheads.models import VoteHead
from voteheads.serializers import VoteHeadSerializer
from .models import Student
from .serializers import StudentSerializer
from streams.models import Stream


class StudentCreateView(SchoolIdMixin, DefaultMixin, generics.CreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        school_id = self.check_school_id(self.request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['school_id'] = school_id

            try:
                self.perform_create(serializer)
            except Exception as exception:
                return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

            created_student = serializer.instance
            if created_student.invoice_Student:
                studentList = []
                studentList.append(created_student)
                #TEST

                try:
                    return createInvoices(school_id, studentList, created_student.current_Year, created_student.current_Term,
                                          created_student.current_Class)
                except Exception as exception:
                    return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Student created successfully'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination  # Use the default pagination class

    def get_queryset(self):
        school_id = self.check_school_id(self.request)
        if not school_id:
            return Student.objects.none()
        self.check_defaults(self.request, school_id)

        queryset = Student.objects.filter(school_id=school_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return JsonResponse({}, status=200)

        current_class = request.GET.get('current_class')
        current_stream = request.GET.get('current_stream')
        student_id = request.GET.get('student_id')

        if current_class:
            queryset = queryset.filter(current_Class = current_class)
        if current_stream:
            queryset = queryset.filter(current_Stream = current_stream)
        if student_id:
            queryset = queryset.filter(id = student_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class StudentDetailView(SchoolIdMixin, DefaultMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return Student.objects.get(id=id)
        except (ValueError, Student.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.validated_data['school_id'] = school_id
            try:
                self.perform_update(serializer)
            except Exception as exception:
                return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Student updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'error': 'Invalid school_id in token'}, status=401)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)


class StudentBalanceDetailView(SchoolIdMixin, DefaultMixin, generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            student = self.get_object()

            school_id = self.check_school_id(request)
            if not school_id:
                return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
            self.check_defaults(self.request, school_id)

            year = request.GET.get('year')
            term = request.GET.get('term')

            if year and year != "" and year != "null":
                if not term or term == "" or term == "null":
                    return Response({'detail': f"Both year and term are required"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    year = AcademicYear.objects.get(id=year)
                except ObjectDoesNotExist:
                    year = None

            if term and term != "" and term != "null":
                if not year or year == "" or year == "null":
                    return Response({'detail': f"Both year and term are required"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    term = Term.objects.get(id=term)
                except ObjectDoesNotExist:
                    term = None

            if not year and not term or term == "" and year == "" or term == "null" and year == "null":
                total_amount_required = Invoice.objects.filter(school_id=school_id, student=student.id).aggregate(total_amount_required=Sum('amount'))['total_amount_required'] or 0.0
                total_amount_paid0 = Receipt.objects.filter(student_id=student.id, school_id=school_id, is_reversed=False).aggregate(total_amount_paid=Sum('totalAmount'))['total_amount_paid'] or 0.0
                total_amount_paid1 = PIKReceipt.objects.filter(student_id=student.id, school_id=school_id, is_posted=True).aggregate(total_amount_paid=Sum('totalAmount'))['total_amount_paid'] or 0.0
                total_amount_paid = Decimal(total_amount_paid0) + Decimal(total_amount_paid1)
            else:
                total_amount_required = Invoice.objects.filter(school_id=school_id, term=term, year=year,student = student.id).aggregate(total_amount_required=Sum('amount'))['total_amount_required'] or 0.0
                total_amount_paid0 = Receipt.objects.filter(student_id=student.id,term=term, year=year, school_id=school_id, is_reversed=False).aggregate(total_amount_paid=Sum('totalAmount'))['total_amount_paid'] or 0.0
                total_amount_paid1 = PIKReceipt.objects.filter(student_id=student.id,term=term, year=year, school_id=school_id, is_posted=True).aggregate(total_amount_paid=Sum('totalAmount'))['total_amount_paid'] or 0.0
                total_amount_paid = Decimal(total_amount_paid0) + Decimal(total_amount_paid1)

            balance = Decimal(total_amount_required) - Decimal(total_amount_paid)

            response_data = {
                'student_id': student.id,
                'balance': balance,
            }

            return Response({"detail": response_data})
        except Exception as exception:
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class StudentSearchByAdmissionNumber(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        admissionNumber = request.GET.get('admission')

        if not admissionNumber or admissionNumber == "" or admissionNumber == "null":
            return Response({'detail': "Admission Number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(school_id = school_id, admission_number=admissionNumber)
        except ObjectDoesNotExist:
            return Response({'detail': "Student with admission number not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(student)
        serialized_data = serializer.data

        return Response({'detail': serialized_data}, status=status.HTTP_200_OK)

class StudentSearchByUID(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        student_id = request.GET.get('student_id')

        if not student_id or student_id == "" or student_id == "null":
            return Response({'detail': "Id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(school_id = school_id, id=student_id)
        except ObjectDoesNotExist:
            return Response({'detail': "Student with Id not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(student)
        serialized_data = serializer.data

        return Response({'detail': serialized_data}, status=status.HTTP_200_OK)


class GetStudentsByClass(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        currentClass = request.GET.get('currentClass')

        if not currentClass or currentClass == "" or currentClass == "null":
            return Response({'detail': "Current Class is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            students = Student.objects.filter(school_id=school_id, current_Class=currentClass).all()
        except Exception as exception:
            return Response({'detail': f"{exception}"}, status=status.HTTP_400_BAD_REQUEST)

        if not students:
            return JsonResponse([], status=200, safe=False)

        for student in students:
            student.school_id = school_id

        serializer = StudentSerializer(students, many=True)
        serialized_data = serializer.data

        return Response({'detail': serialized_data}, status=status.HTTP_200_OK)


class GetStudentInvoicedVotehead(SchoolIdMixin, DefaultMixin, generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        student = self.get_object()

        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        year = request.GET.get('year')
        term = request.GET.get('term')

        current_academic_year = currentAcademicYear(school_id)
        current_term = currentTerm(school_id)
        if current_academic_year is None or current_term is None:
            return Response({'detail': 'Both Current Academic Year and Current Term must be set for school first'},
                            status=status.HTTP_200_OK)

        try:
            year = get_object_or_404(AcademicYear, id=year) if year and year != "" and year != "null" else current_academic_year
            term = get_object_or_404(Term, id=term) if term and term != "" and term != "null" else current_term
        except Exception as exception:
            return Response({'detail': exception}, status=status.HTTP_400_BAD_REQUEST)

        payload = []

        invoiceList = Invoice.objects.filter(
            student_id=student.id,
            term=term,
            year=year,
            school_id=school_id
        )

        for invoice in invoiceList:
            votehead = invoice.votehead

            receiptAmount = Collection.objects.filter(receipt__term=term, receipt__year=year, votehead=votehead, school_id=school_id,student=student, receipt__is_reversed=False).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
            pikAmount = PIKReceipt.objects.filter(term=term, year=year, school_id=school_id, student=student, is_posted = True).aggregate(Sum('totalAmount'))['totalAmount__sum'] or Decimal(0)

            amountpaid = Decimal(pikAmount) + Decimal(receiptAmount)
            required_amount  = invoice.amount - amountpaid
            invoiced_amount = invoice.amount

            payload.append(
                {
                    "votehead": VoteHeadSerializer(votehead).data,
                    "name": votehead.vote_head_name,
                    "amount_paid": amountpaid,
                    "required_amount": required_amount,
                    "invoiced_amount": invoiced_amount,
                }
            )


        return Response({"detail": payload})




class UploadStudentCreateView(SchoolIdMixin, DefaultMixin, generics.CreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        school_id = self.check_school_id(self.request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)


        classes = request.GET.get('classes')
        stream = request.GET.get('stream')
        fileid = request.GET.get('fileid')

        try:
            currentTerm = Term.objects.get(is_current=True, school_id = school_id)
        except ObjectDoesNotExist:
            return Response({'detail': f"Current Term not set for school"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            currentYear = AcademicYear.objects.get(is_current=True, school_id=school_id)
        except ObjectDoesNotExist:
            return Response({'detail': f"Current Year not set for school"}, status=status.HTTP_400_BAD_REQUEST)


        if not classes or classes == "" or classes == "null":
            return Response({'detail': f"Student class is a must"}, status=status.HTTP_400_BAD_REQUEST)
        if not fileid or fileid == "" or fileid == "null":
            return Response({'detail': f"Csv file is a must"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = SchoolImage.objects.get(id=fileid)
        except ObjectDoesNotExist:
            return Response({'detail': f"This file does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            theclass = Classes.objects.get(id=classes)
        except ObjectDoesNotExist:
            return Response({'detail': f"This class does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            theStream = Stream.objects.get(id=stream)
        except ObjectDoesNotExist:
            return Response({'detail': f"This stream does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file.document)  # Assuming the path attribute contains the file path
        except Exception as e:
            return Response({'detail': f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ['FIRST NAME', 'LAST NAME', 'GENDER', 'ADMNO', 'GUARDIAN NAME',
                            'GUARDIAN PHONE', 'BOARDING STATUS', 'ADMISSION DATE']

        try:
            with transaction.atomic():
                # Iterate through rows
                for position, row in df.iterrows():
                    # Check if all required columns exist
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        return Response({'detail': f"Missing required columns: {', '.join(missing_columns)} in the Excel file"},
                            status=status.HTTP_400_BAD_REQUEST)

                    non_empty_columns = [col for col in required_columns if
                                         pd.isna(row[col]) and col not in ['guardian_name', 'guardian_phone']]

                    if non_empty_columns:
                        return Response({'detail': f"Column(s) {', '.join(non_empty_columns)} cannot be empty for student at row {position}"},
                            status=status.HTTP_400_BAD_REQUEST)

                    # Process the extracted data as needed
                    last_name = str(row['LAST NAME'])
                    first_name = str(row['FIRST NAME'])
                    gender = str(row['GENDER'])
                    admission_number = str(row['ADMNO'])
                    guardian_name = str(row['GUARDIAN NAME'])
                    guardian_phone = str(row['GUARDIAN PHONE'])
                    boarding_status = str(row['BOARDING STATUS'])
                    date_of_admission = str(row['ADMISSION DATE'])

                    Student.objects.create(
                        first_name = first_name,
                        last_name = last_name,
                        gender = gender,
                        admission_number = admission_number,
                        date_of_admission = date_of_admission,
                        guardian_name = guardian_name,
                        guardian_phone = guardian_phone,
                        boarding_status = boarding_status,
                        school_id = school_id,
                        current_Class = theclass,
                        current_Year = currentYear,
                        current_Term = currentTerm,
                        current_Stream = theStream
                    )

        except Exception as exception:
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


        return Response({'detail': 'Students created successfully'}, status=status.HTTP_201_CREATED)



class UploadStudentBalancesView(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def post(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        try:
            current_financial_year = FinancialYear.objects.get(school=school_id, is_current=True)
        except ObjectDoesNotExist:
            return Response({'detail': f"Current financial year has not been set for this school"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            currency = Currency.objects.get(school=school_id, is_default=True)
        except Currency.DoesNotExist:
            currency = None
            return Response({"detail": "Default Currency Not Set For This School"},
                            status=status.HTTP_400_BAD_REQUEST)

        current_academic_year = currentAcademicYear(school_id)
        current_term = currentTerm(school_id)
        if not current_academic_year or not current_term:
            return Response({'detail': f"Both current academic year and current term are required"}, status=status.HTTP_400_BAD_REQUEST)

        due_date = request.GET.get('due_date')
        template_id = request.GET.get('template_id')

        if not template_id or template_id == "" or template_id == "null":
            return Response({'detail': f"Template Is A Must"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = SchoolImage.objects.get(id=template_id)
        except ObjectDoesNotExist:
            return Response({'detail': f"This file does not exist"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            df = pd.read_excel(file.document)
        except Exception as e:
            return Response({'detail': f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


        required_columns = ['ADMNO', 'NAME', 'AMOUNT']

        try:
          with transaction.atomic():
              for position, row in df.iterrows():
                  missing_columns = [col for col in required_columns if col not in df.columns]
                  if missing_columns:
                      return Response(
                          {'detail': f"Missing required columns: {', '.join(missing_columns)} in the Excel file"},
                          status=status.HTTP_400_BAD_REQUEST)

                  non_empty_columns = [col for col in required_columns if
                                       pd.isna(row[col]) and col not in ['guardian_name', 'guardian_phone']]

                  if non_empty_columns:
                      return Response({ 'detail': f"Column(s) {', '.join(non_empty_columns)} cannot be empty for student at row {position}"},
                                      status=status.HTTP_400_BAD_REQUEST)

                  # Process the extracted data as needed
                  admission_number = str(row['ADMNO'])
                  student_name = str(row['NAME'])
                  amount = Decimal(row['AMOUNT'])

                  try:
                      student = Student.objects.get(admission_number=admission_number)
                  except ObjectDoesNotExist:
                      return Response({'detail': f"Student {student_name} of admission number {admission_number} not found"}, status=status.HTTP_400_BAD_REQUEST)

                  try:
                      invoicable_votehead = VoteHead.objects.get(is_Arrears_Default=True, school_id= school_id)
                  except ObjectDoesNotExist:
                      return Response({'detail': f"This school does not have an arrears default votehead set!"}, status=status.HTTP_400_BAD_REQUEST)

                  description = invoicable_votehead.vote_head_name
                  amount = amount
                  term = current_term
                  year = current_academic_year
                  classes = student.current_Class
                  school_id = school_id
                  votehead = invoicable_votehead
                  exists_query = Invoice.objects.filter(votehead__id=votehead.id, term=term, year=year, student=student, school_id=school_id)

                  invoice_no = generate_unique_code()

                  if exists_query.exists():
                      invoice = exists_query[0]
                      invoice.amount = invoice.amount + Decimal(amount)
                      invoice.save()
                  else:
                      invoice = Invoice(
                          issueDate=timezone.now().date(),
                          invoiceNo=invoice_no,
                          amount=amount,
                          paid=0.00,
                          due=amount,
                          description=description,
                          student=student,
                          term=term,
                          year=year,
                          classes=classes,
                          currency=currency,
                          school_id=school_id,
                          votehead=votehead
                      )
                      invoice.save()

          return Response({'detail': f"Balances were uploaded successfully"}, status=status.HTTP_200_OK)

        except Exception as exception:
          return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)







class UploadSingleStudentBalance(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def post(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        try:

            try:
                current_financial_year = FinancialYear.objects.get(school=school_id, is_current=True)
            except ObjectDoesNotExist:
                return Response({'detail': f"Current financial year has not been set for this school"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                currency = Currency.objects.get(school = school_id, is_default=True)
            except Currency.DoesNotExist:
                currency = None
                return Response({"detail": "Default Currency Not Set For This School"}, status=status.HTTP_400_BAD_REQUEST)

            current_academic_year = currentAcademicYear(school_id)
            current_term = currentTerm(school_id)
            if not current_academic_year or not current_term:
                return Response({'detail': f"Both current academic year and current term are required"}, status=status.HTTP_400_BAD_REQUEST)

            due_date = request.GET.get('due_date')
            student_id = request.GET.get('student_id')
            total_balance = request.GET.get('total_balance')

            if not student_id or student_id == "" or student_id == "null" or not total_balance or total_balance == "" or total_balance == "null":
                return Response({'detail': f"Values Due Date, Student And Total Balance are all required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
              student = Student.objects.get(id=student_id)
            except ObjectDoesNotExist:
              return Response({'detail': "Student does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            try:
              invoicable_votehead = VoteHead.objects.get(is_Arrears_Default=True, school_id=school_id)
            except ObjectDoesNotExist:
              return Response({'detail': f"This school does not have an arrears default votehead set!"}, status=status.HTTP_400_BAD_REQUEST)

            description = invoicable_votehead.vote_head_name
            amount = Decimal(total_balance)
            term = current_term
            year = current_academic_year
            classes = student.current_Class
            school_id = school_id
            votehead = invoicable_votehead
            exists_query = Invoice.objects.filter(school_id = school_id, votehead__id=votehead.id, term=term, year=year, student=student)

            invoice_no = generate_unique_code()

            if exists_query.exists():
              invoice = exists_query[0]
              invoice.amount = invoice.amount + Decimal(amount)
              invoice.save()
            else:
              invoice = Invoice(
                  issueDate=timezone.now().date(),
                  invoiceNo=invoice_no,
                  amount=amount,
                  paid=0.00,
                  due=amount,
                  description=description,
                  student=student,
                  term=term,
                  year=year,
                  classes=classes,
                  currency=currency,
                  school_id=school_id,
                  votehead=votehead
              )
              invoice.save()

        except Exception as exception:
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': f"Balances were uploaded successfully"}, status=status.HTTP_200_OK)






class UpdateStudentGroupsAPIView(generics.UpdateAPIView, SchoolIdMixin):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def post(self, request, *args, **kwargs):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)

        student_ids = request.data.get('student_ids', [])
        group_ids = request.data.get('group_ids', [])
        action = request.data.get('action')

        if not action or not action in ['add', 'remove']:
            return Response({"detail": "Invalid action. Use 'add' or 'remove'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            students = Student.objects.filter(id__in=student_ids, school_id=school_id)
            groups = SchoolGroup.objects.filter(id__in=group_ids, school_id=school_id)
        except Student.DoesNotExist:
            return Response({"detail": "Invalid student ID."}, status=status.HTTP_400_BAD_REQUEST)
        except SchoolGroup.DoesNotExist:
            return Response({"detail": "Invalid group ID."}, status=status.HTTP_400_BAD_REQUEST)

        for student in students:
            student_groups = set(student.groups)

            for group in groups:
                if action == 'add':
                    if group.id not in student_groups:
                        student_groups.add(str(group.id))
                elif action == 'remove':
                    student_groups.discard(str(group.id))

            student.groups = list(student_groups)
            student.save()

        return Response({"detail": "Students Groups updated successfully."}, status=status.HTTP_200_OK)





class StudentDeleteAllView(SchoolIdMixin, DefaultMixin, generics.DestroyAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Student.objects.none()

    def delete(self, request, *args, **kwargs):
        school_id = request.query_params.get('school_id')
        if not school_id:
            return JsonResponse({"message": "school_id is required"}, status=400)

        self.check_defaults(request, school_id)
        queryset = Student.objects.filter(school_id=school_id)

        if not queryset.exists():
            return JsonResponse({"message": "No students to delete"}, status=200)

        total_count = queryset.count()
        deleted_count = 0
        errors = []

        for student in queryset:
            try:
                student.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(str(e))

        return JsonResponse({
            "message": f"Deleted {deleted_count} out of {total_count} students",
            "errors": errors
        }, status=200)

