# Payment Gateway adapter for TBC Bank

#### შესავალი (მოკლე აღწერა)
მოცემული Python package წარმოადგენს ადაპტერს TBC-ის ონლაინ გადახდებისთვის, სადაც მოცემულია ყველა საჭირო ნაწილი, რომელიც მომხმარებელს საშუალებას მისცემს სერთიფიკატისა და პაროლის არსებობის შემთხვევაში მარტივად მოახდინოს დოკუმენტაციაში აღწერილი API მეთოდების გამოყენება. 

#### დაყენება / ინსტალაცია & python-ის ვერსია

package-ი დატესტილია და მუშაობს python3-თვის (>3.4). წესით, python2-ზეც არ უნდა ჰქონდეს პრობლემა, მაგრამ დარწმუნებით ვერ გეტყვით :).

package-ის დაყენების 2 გზა არსებობს:

1) ჩამოტვირთეთ პირდაპირ გიტჰაბიდან და გაუშვით `python3 setup.py	install`
2) pip-ის გამოყენებით `pip3 install tbc_adapter`

happy coding!

#### API-ს იმპლემენტირებული მეთოდები
TBC API-სთან საურთიერთობოდ იმპლემენტირებულია შემდეგი 7 ძირითადი მეთოდი, რომელიც ქვემოთ არის მოცემული, ხოლო სანამ მეთოდების აღწერაზე გადავალ, საჭიროა შევქმნათ ჩვენი კლასი, რომლის მშობელიც იქნება `tbc_adapter.adapters.TBCAdapter` და იმპლემენტაცია გავუკეთოთ 2 property-ს. ქვემოთ არის მოცემული მაგალითი რეალური მუშა გარემოდან, რომლითაც შეგიძლიათ იხელმძღვანელოთ:

```python
import os
from tbc_adapter.adapters import TBCAdapter
from tbc_adapter.p12_converter import generate_pems

# ცვლადში არის მისამართი სადაც ცხოვრობს TBC-გან მოწოდებული .p12 გაფართოების ფაილი 
# და იცხოვრებენ დაგენერირებული .pem გაფართოების ფაილები
CERTIFICATE_DIR = "/abs/path/to/certificate/"
# ცვლადში არის .p12 სერთიფიკატის პაროლი, რომელიც მოწოდებულია TBC ბანკის მიერ
CERTIFICATE_PSWD = "secret"

class MyFancyAdapter(TBCAdapter):
    @property
    def pem_paths(self):
        p12_path = os.path.join(CERTIFICATE_DIR, "certificate.p12")
        cert_path = os.path.join(CERTIFICATE_DIR, "certificate.pem")
        key_path = os.path.join(CERTIFICATE_DIR, "privatekey.pem")
        if not (os.path.isfile(cert_path) or os.path.isfile(key_path)):
            cert_path, key_path = generate_pems(p12_path,
                                                CERTIFICATE_PSWD,
                                                CERTIFICATE_DIR)
        return (cert_path, key_path)

    @property
    def service_url(self):
        return "https://securepay.ufc.ge:18443/ecomm2/MerchantHandler"
```

პირველი property - `pem_paths` აბრუნებს .pem ფორმატში გადაყვანილ სერთიფიკატს და მის გასაღებს, ხოლო თუ ეს ორი კომპონენტი დირექტორიაში არ არის, მაშინ აგენერირებს, ინახავს დირექტორიაში და აბრუნებს მისამართებს. ხოლო, property `service_path` აბრუნებს ბანკის სერვისის მისამართს.

ახლა შეგვიძლია გადავიდეთ ჩვენი `MyFancyAdapter` კლასის გამოყენებაზე და სათითაოდ გავიაროთ იმპლემენტირებული მეთოდები:

#### 1) ტრანზაქციის id-ის დაგენერირება (თანხის ჩამოჭრით)

აბრუნებს: TRANSACTION_ID   
გვჭირდება: კლიენტის IP მისამართი, გადასახდელი თანხა (თეთრებში)

```python
client_ip = "xxx.xxx.xxx.xxx"
amount_in_tetri = 3000
    
adapter = MyFanceAdapter(client_ip)
result = adapter.get_transaction_id(amount)
   	
print(result)  # >>> {"TRANSACTION_ID": "xyz"}
```

#### 2) ტრანზაქციის სტატუსის გაგება

აბრუნებს: RESULT, RESULT_CODE, CARD_NUMBER   
გვჭირდება: კლიენტის IP მისამართი, ტრანზაქციის ID

```python
client_ip = "xxx.xxx.xxx.xxx"
trans_id = "xyz"
    
adapter = MyFanceAdapter(client_ip, trans_id)
result = adapter.get_transaction_status()
   	
print(result)  # >>> {"RESULT": "x", "RESULT_CODE": "y", CARD_NUMBER: "z"}
```

##### 3) დღის დახურვის ოპერაცია

აბრუნებს: RESULT, RESULT_CODE   
გვჭირდება: კლიენტის IP მისამართი (ამ შემთხვევაში ჩვენი სერვერის)

```python
client_ip = "xxx.xxx.xxx.xxx"
    
adapter = MyFanceAdapter(client_ip)
result = adapter.end_business_day()
   	
print(result)  # >>> {"RESULT": "x", "RESULT_CODE": "y"}
```

##### 4) პრე-ავტორიზაცია (თანხის დაბლოკვა)

აბრუნებს: TRANSACTION_ID   
გვჭირდება: კლიენტის IP მისამართი, თანხა (თეთრებში, რომელიც დაებლოკება მომხმარებელს)

```python
client_ip = "xxx.xxx.xxx.xxx"
amount = 3000
    
adapter = MyFanceAdapter(client_ip)
result = adapter.get_preauthed_transaction_id(amount)
   	
print(result)  # >>> {"TRANSACTION_ID": "xyz"}
```

##### 5) პრე-ავტორიზებული ტრანზაქციის კომიტი (თანხის ჩამოჭრა)

აბრუნებს: RESULT, RESULT_CODE, CARD_NUMBER   
გვჭირდება: კლიენტის IP მისამართი, თანხა (თეთრებში), ტრანზაქციის ID

```python
client_ip = "xxx.xxx.xxx.xxx"
trans_id = "xyz"
amount = 3000
    
adapter = MyFanceAdapter(client_ip, trans_id)
result = adapter.commit_preauthed(amount)
   	
print(result)  # >>> {"RESULT": "x", "RESULT_CODE": "y", CARD_NUMBER: "z"}
```

##### 6) ტრანზაქციის რევერსალი
აბრუნებს: RESULT, RESULT_CODE   
გვჭირდება: კლიენტის IP მისამართი, ტრანზაქციის ID

```python
client_ip = "xxx.xxx.xxx.xxx"
trans_id = "xyz"
    
adapter = MyFancyAdapter(client_ip, trans_id)
result = adapter.reverse_transaction()
    
print(result)  # >>> {"RESULT_CODE": "x", "RESULT": "y"}
```

##### 7) ტრანზაქციის რეფანდი
აბრუნებს: RESULT, RESULT_CODE   
გვჭირდება: კლიენტის IP მისამართი, ტრანზაქციის ID, თანხა (თეთრებში) (არასავალდებულო)

```python
client_ip = "xxx.xxx.xxx.xxx"
trans_id = "xyz"
amount = 3000
    
adapter = MyFancyAdapter(client_ip, trans_id)
# თუ ნაწილობრივი refund-ს ვანხორციელებთ
result = adapter.refund_transaction(amount)
# თუ სრულ refund-ს ვანხორციელებთ
result = adapter.refund_transaction()
    
print(result)  # >>> {"RESULT": "x", "RESULT_CODE": "y"}
```

#### API მეთოდებიდან დაბრუნებული ცვლადების მოდიფიკაცია
ყველა API მეთოდი, უკან აბრუნებს ლექსიკონს (dict), რომელიც შეიცავს ბანკისგან დაბრუნებულ მნიშვნელობებს. მაგალითად, პრეავტორიზაციის კომიტი უკან აბრუნებს არამარტო RESULT_CODE, RESULT-სა და CARD_NUMBER-ს, არამედ, დამატებით RRN-სა და APPROVAL_CODE-ს, რომელიც შეიძლება საერთოდ არ გამოვიყენოთ, მაგრამ შესაძლებელია რაღაც მომენტში საჭირო გახდეს, ამიტომ თუ გვსურს ზემოთ აღნიშნული 2 მნიშვნელობაც მივიღოთ პირველ სამთან ერთად უბრალოდ საჭიროა შემდეგი მოდიფიკაცია:

```python
# imports

class MyFancyAdapter(TBCAdapter):
	#  implementations & definitions
    commit_preauthed.api_out = ("RESULT", "RESULT_CODE", "CARD_NUMBER", "RRN", "APPROVAL_CODE")
```

თითოეულ API მეთოდს გააჩნია api_out list/tuple, რომელიც ერთგვარი მეტა ინფორმაციაა, რა ცვლადები უნდა დააბრუნოს ადაპტერმა უკან კონკრეტული მეთოდებისთვის. თუ `api_out` სიის მსგავს ობიექტში არსებული გასარები ბანკიდან დაბრუნებულ პასუხში არ აღმოჩნდა, მაშინ მისი მნიშვნელობა იქნება `None`.
