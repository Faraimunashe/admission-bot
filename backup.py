elif "quote" in msg:
        #string = "This is a test string with Bmamectin x1, Penstrep x3, Multidip x6"
        string = msg
        pattern = r"[Xx][1-9][0-9]*"
        total_price = 0.00
        quotations = []
        randomstring = randomword(16)
        docname = str(randomstring) + '.pdf'
        css = 'static/style.css'
        

        matches = re.findall(pattern, string)
        prodpattern = rf'(\w+)\s*(?:\b(?:{"|".join(matches)})\b)'
        prodmatch = re.findall(prodpattern, string)
        #print(prodmatch, matches)

        if prodmatch:
            i=0
            for sch in prodmatch:
                quote = {}
                prod = Product.query.filter(Product.name.like(sch)).first()
                if prod != None:
                    price = prod.price * int(integer(matches[i]))
                    total_price = Decimal(total_price) + Decimal(price)
                    quote = {'name':prod.name, 'unit':prod.price, 'qty':matches[i], 'total':price}
                    quotations.append(quote)
                    i=i+1
                    
                else:
                    i=i+1
                
        else:
            custom_quote = "\n Could not locate products in your request. \n"
        

        current_dateTime = datetime.now()
        pdf_content = render_template('quote.html', quotations=quotations, total=total_price, name=name, phone=phone, current_dateTime=current_dateTime) 
        configpath = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

        static_dir = os.path.abspath('static')
        pdf_file = pdfkit.from_string(pdf_content, configuration=configpath, css=css)
        with open(os.path.join(static_dir, docname), 'wb') as f:
            f.write(pdf_file)


        reply.media("static/"+docname)
    else:
        if bot.menu == "main-branch":
            latitude = request.form.get('Latitude')
            longitude = request.form.get('Longitude')

            if latitude == None or longitude == None:
                reply.body("*Please us a valid location*")
            else:
                branches = Branch.query.all()
                result = branches_schema.dump(branches)
                # print(branches)
                # print("\n New Line here \n")
                # print(result)
                user_location = (latitude, longitude)
                distance_array = []
                for res in branches:
                    branch_location = (res.latitude, res.longitude)
                    distance = find(user_location, branch_location)
                    distance_array.append(distance)
                
                pos = distance_array.index(min(distance_array))
                print(branches[pos].name)
                bot.menu = 'main'
                db.session.commit()
                reply.body("*THE NEAREST BRANCH:*\n *"+branches[pos].name+"*\n *address:* "+branches[pos].address+"\n *telephone:* "+branches[pos].telephone+"\n *mobile:* "+branches[pos].mobile+"\n *email:* "+branches[pos].email)

        elif(greeting(msg) != None):
            bot.menu = 'main'
            db.session.commit()

            reply.body(greeting(msg))

        elif(list_quotes(msg) != None):
            bot.menu = 'main'
            db.session.commit()

            reply.body(list_quotes(msg))

        else:
            qstn = msg
            answer = nlp(qstn)

            print(answer)
            reply.body(answer)

