## 디렉토리 설명
#### *_interface
    - 프로그램에서 직접 사용되지 않지만, 편하게 데이터를 확인/수정할 수 있게 하기 위한 파일입니다.
    - 제품 정보, 매출 정보 등을 정해진 양식에 맞게 저장합니다.
    - 양식에서 벗어난 데이터가 있을 경우, 프로그램을 실행시키지 않습니다.
    - 양식은 아래와 같습니다.
        1. 모든 row의 column 수는 항상 같아야 합니다.
        2. 각 row는 개행 문자(\n, ENTER)로 구분됩니다.
        3. 각 row의 column은 delimiter로 구분됩니다.
        4. delimiter: 한 row 안에서 각 column의 데이터를 구분하는 하나의 문자입니다.
        5. 각 column을 구성하는 데이터는 적절히 입력되어야 합니다(ex. 할인율: 0 이상 100 이하의 수)
        6. 각 column 데이터의 앞 뒤에 존재하는 공백 문자는 자동으로 삭제됩니다.

#### *_datas
    - 데이터를 조작하기 위해 프로그램이 직접 사용하는 python pickle 파일입니다.
    - 파일마다 정해진 Data Type이 존재합니다.

## 파일 설명
#### 1. product_interface
##### delimiter : ","
##### description : 제품의 정보를 저장하기 위한 파일로, 프로그램 시작시 해당 파일을 토대로 제품 정보가 갱신됩니다.
##### column
    0. 제품 코드  [정수, int, 0 이상, 중복 불가능]
    1. 제품명     [문자열, str, 중복 불가능]
    2. 단가       [정수, int, 0 이상]
    3. 할인율     [정수, int, 0~100%]
    
#### 2. product_datas
##### delimiter : ","
##### description : 제품 코드(product_code)를 key로 하고, 제품명(name), 단가(price), 할인율(discount_rate)을 member로 가지는 Product 클래스를 value로 하는 dictionary입니다.