from drf_yasg import openapi

# response for total expenses endpoint
response_total_expenses_schema_dict = {
    "200": openapi.Response(
        description="Total expenses",
        examples={
            "application/json": {
                "start_date": "start_date",
                "end_date": "end_date",
                "category": "category_uuid or all",
                "expenses": [
                    {
                        "category_uuid": "category_uuid",
                        "category_name": "category_name",
                        "cat_expenses": [
                            {
                                "date": "date",
                                "category_uuid": "category_uuid",
                                "category_name": "category_name",
                                "short_description": "short_description",
                                "currency_code": "amount",
                            },
                        ],
                    },
                ],
            }
        },
    ),
}
