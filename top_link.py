
class GetTopLinks(APIView):
    permission_classes = (AllowAny,)
    queryset = Lead.objects.filter(
        listing__published=True,
        listing__status=ListingChoices.PUBLISHED,
        procurement_category=ProcurementCategoryOptions.ASSURED,
        listing__sold=False,
        tags__name__in=["inventory-available-for-sale", "dummy-tag"]
    ).select_related('profile', 'profile__make', 'profile__model', 'listing_price')
    pricing_table_size = 10

    def validate_and_get_attributes(self, filter_object):
        priority_list = ['min_price', 'max_price', 'model', 'min_year', 'fuel_type', 'transmission',
                         'max_mileage', 'color', 'make', 'body_type']
        attr = []
        if filter_object.keys().__contains__('city') and len(filter_object['city']) == 1:
            attr.append('city')
            for i in priority_list:
                if filter_object.keys().__contains__(i) and len(filter_object[i]) == 1:
                    attr.append(i)
                    break
        return attr

    def get_configuration(self, filter_object):
        received_attributes = self.validate_and_get_attributes(filter_object)
        filters = []
        if 'city' in received_attributes:
            url_categories = config['default']
            received_attributes.remove('city')
            filters.append('city')
            for i in received_attributes:
                filters.append(i)
                url_categories = config[i]
                break
        else:
            url_categories = config['empty']
        return filters, url_categories

    def generate_links_by_make(self, queryset, city):
        makes = []
        for query in queryset:
            if query.make.name is not None and not (query.make.name in makes):
                makes.append(query.make.name)
        makes = makes[:40]
        makes_with_display_name = Make.objects.filter(name__in=makes).values('name', 'display_name')
        result = []
        val = {}
        for i in makes_with_display_name:
            val["display_name"] = 'Used ' + i['display_name'] + ' Cars in ' + city.title()
            val["url"] = '/used-' + i['name'] + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_model(self, queryset, city):
        models = []
        for query in queryset:
            if query.model.name is not None and not (query.model.name in models):
                models.append(query.model.name)
        models = models[:40]
        models_with_display_name = Model.objects.filter(name__in=models).values('name', 'display_name')
        result = []
        val = {}
        for i in models_with_display_name:
            val["display_name"] = 'Used ' + i['display_name'] + ' cars in ' + city.title()
            val["url"] = '/used-' + i['name'] + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_body_type(self, queryset, city):
        body_types_distinct = []
        for query in queryset:
            if query.variant.body_type is not True and not (query.variant.body_type in body_types_distinct):
                body_types_distinct.append(query.variant.body_type)
        valid_body_types = ['hatchback', 'sedan', 'suv']
        body_types = []
        for x in body_types_distinct:
            if x in valid_body_types:
                body_types.append(x)
        body_types = body_types[:40]
        display_names = {}
        for i in body_types:
            if i == 'suv' or i == 'muv':
                display_names[i] = i.upper()
            else:
                display_names[i] = i.capitalize()
        result = []
        val = {}
        for i in body_types:
            val["display_name"] = 'Used ' + display_names[i] + ' cars in ' + city.title()
            val["url"] = '/used-' + i + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_transmission(self, queryset, city):
        transmissions = []
        for query in queryset:
            if not (query.transmission_type in transmissions):
                transmissions.append(query.transmission_type)
        transmissions = transmissions[:40]
        result = []
        val = {}
        for i in transmissions:
            val["display_name"] = 'Used ' + i.capitalize() + ' cars in ' + city.title()
            val["url"] = '/used-' + i + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_color(self, queryset, city):
        colors = []
        for query in queryset:
            if query.color is not None and not (query.color in colors):
                colors.append(query.color)
        colors = colors[:40]
        result = []
        val = {}
        for i in colors:
            val["display_name"] = 'Used ' + i + ' cars in ' + city.title()
            val["url"] = '/used-' + i + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_fuel_type(self, queryset, city):
        fuel_types = []
        for query in queryset:
            if not (query.fuel_type in fuel_types):
                fuel_types.append(query.fuel_type)
        fuel_types = fuel_types[:40]
        result = []
        val = {}
        for i in fuel_types:
            if i == 'petrol+cng':
                i = 'cng'
            val["display_name"] = 'Used ' + i.capitalize() + ' cars in ' + city.title()
            val["url"] = '/used-' + i + '-cars-in-' + city + '/s/'
            result.append(val)
            val = {}
        return result

    def generate_links_by_mileage(self, queryset, city):
        result = []
        if len(queryset) > 0:
            mileage_points = ['10000', '30000', '50000', '75000', '100000']
            val = {}
            for i in mileage_points:
                val["display_name"] = 'Used cars under ' + i + ' KMs in ' + city.title()
                val["url"] = '/used-cars-under-' + i + '-kms-in-' + city + '/s/'
                result.append(val)
                val = {}
        return result

    def generate_links_by_year(self, queryset, city):
        result = []
        if len(queryset) > 0:
            year_points = ['2009', '2011', '2013', '2017']
            val = {}
            for i in year_points:
                val["display_name"] = 'Used cars from ' + i + ' and above in ' + city.title()
                val["url"] = '/used-cars-from-' + i + '-in-' + city + '/s/'
                result.append(val)
                val = {}
        return result

    def generate_links_by_price(self, queryset, city, min_price=None, max_price=None):
        result = []
        if len(queryset) > 0:
            price_points = [['2', '3'], ['3', '4'], ['4', '5'], ['5', '6'], ['6', '7'], ['7', '10']]
            val = {}
            if min_price is None and max_price is None:
                val["display_name"] = 'Used cars under 2 Lakhs in ' + city.title()
                val["url"] = '/used-cars-under-2-lakh-rs-in-' + city + '/s/'
                result.append(val)
                val = {}
                for i in price_points:
                    val["display_name"] = 'Used cars from ' + i[0] + ' lakhs to ' + i[1] + ' lakhs in ' + city.title()
                    val["url"] = '/used-cars-over-' + i[0] + '-lakh-rs-under-' + i[
                        1] + '-lakh-rs-in-' + city + '/s/'
                    result.append(val)
                    val = {}
                val["display_name"] = 'Used cars from 10 Lakhs in ' + city.title()
                val["url"] = '/used-cars-over-10-lakh-rs-in-' + city + '/s/'
                result.append(val)
        return result

    def prepare_pricing_data(self, lead):
        pricing_row = {
            'make': {'display_name': lead.get('make_name'), 'key': lead.get('make_key')},
            'model': {'display_name': lead.get('model_name'), 'key': lead.get('model_key')},
            'fuel_type': {'display_name': lead.get('fuel_type', "").capitalize(), 'key': lead.get('fuel_type')},
            'transmission': {'display_name': lead.get('transmission', "").capitalize(), 'key': lead.get('transmission')},
            'price': lead.get('price'),
            'count': lead.get('count')
        }
        return pricing_row

    def generate_pricing_table(self, filter_object):
        for key, value in filter_object.items():
            filter_object[key] = ",".join(value)
        queryset = self.queryset.exclude(tags__name__in=["booked-inventory"])
        filtered_queryset = LeadListingFilterV1(filter_object, queryset).qs
        queryset = filtered_queryset.values(
            make_name=F('profile__make__display_name'), make_key=F('profile__make__name'),
            model_name=F('profile__model__display_name'), model_key=F('profile__model__name'),
            fuel_type=F('profile__fuel_type'),
            transmission=F('profile__variant__transmission')
        ).annotate(price=Min('listing_price__value'), count=Count('id')).order_by('-count')[:self.pricing_table_size]
        pricing_table = [self.prepare_pricing_data(qs) for qs in queryset]
        return pricing_table

    def get(self, request):
        filter_object = request.GET.get('filter_object')
        if filter_object:
            try:
                filter_object = json.loads(filter_object)
            except Exception:
                filter_object = {}
        else:
            filter_object = {}
        configuration = self.get_configuration(filter_object)
        filters = configuration[0]
        url_categories = configuration[1]
        lead_profile_ids = self.queryset.values_list('profile_id', flat=True)
        queryset = LeadProfile.objects.filter(pk__in=lead_profile_ids).select_related("make", "model", "variant",
                                                                                      "city")
        for i in filters:
            if i == 'make':
                queryset = queryset.filter(make__name=filter_object["make"][0])
            elif i == 'city':
                city = filter_object["city"][0]
                if city == "delhi-ncr":
                    queryset = queryset.filter(city__name__in=['noida', 'gurgaon', 'delhi'])
                else:
                    queryset = queryset.filter(city__name=city)
            elif i == 'model':
                queryset = queryset.filter(model__name=filter_object["model"][0])
            elif i == 'body_type':
                queryset = queryset.filter(variant__body_type=filter_object["body_type"][0])
            elif i == 'transmission':
                queryset = queryset.filter(transmission_type=filter_object["transmission"][0])
            elif i == 'max_mileage':
                queryset = queryset.filter(mileage__lte=filter_object["max_mileage"][0])
            elif i == 'color':
                queryset = queryset.filter(color=filter_object["color"][0])
            elif i == 'min_year':
                queryset = queryset.filter(make_year__gte=filter_object["min_year"][0])
        result = {"top_links": get_top_links()}
        related_links = {}
        queryset_cash = list(queryset)
        for i in url_categories:
            if i == 'make':
                related_links["make"] = self.generate_links_by_make(queryset_cash, city)
            elif i == 'model':
                related_links["model"] = self.generate_links_by_model(queryset_cash, city)
            elif i == 'body_type':
                related_links["body_type"] = self.generate_links_by_body_type(queryset_cash, city)
            elif i == 'fuel_type':
                related_links["fuel_type"] = self.generate_links_by_fuel_type(queryset_cash, city)
            elif i == 'transmission':
                related_links["transmission"] = self.generate_links_by_transmission(queryset_cash, city)
            elif i == 'max_mileage':
                related_links["mileage"] = self.generate_links_by_mileage(queryset_cash, city)
            elif i == 'color':
                related_links["color"] = self.generate_links_by_color(queryset_cash, city)
            elif i == 'price':
                related_links["price"] = self.generate_links_by_price(queryset_cash, city)
            elif i == 'min_year':
                related_links["year"] = self.generate_links_by_year(queryset_cash, city)
        result["related_links"] = related_links
        result["pricing_table"] = self.generate_pricing_table(filter_object)
        return Response(result)
