#put all cases as constants.py has variable special cases -- set with the cases, have the regular expressions there, constandts so keep them there, import here

date1='\d{1,2}[/]\d{1,2}[/]\d{4}'
date2='\d{1,2,3}[-]\d{1,2}[-]\d{4}'
date3='\S{4,9}[ ]\d{1,2}[,][ ]\d{4}'
date4='\d{1,2}[-]\d{1,2}[-]\d{4}'

date_format='\S{4,9}[_]\d{1,2}[_]\d{4}'

date_month='(\S{4,9})'
date_day='\S{4-9}(\w|\d|\s)[,]'

date_comma='\w([,])'

file_ext='(\w+)[.](pdf|html|doc|xls)'

abbrev='(\w)[.]+'

email ='[\w]+@[\w]+[.]'

hyphen='(\w+)[-]'

#hyphen='([a-z]+)[-]'

hyphen_general='[-]'

period_alpha='[.]+([a-z]+)'

digalpha='(([0-9]+)[-]([a-z]+))+'

alphadig='(([a-z]+)[-]([0-9]))+'

ip='(\d{2,3}[.]\d{2,3}[.]\d{2,3}[.]\d{2,3})'

url='[www.]\w+[.](com|edu|net)'

currency='[$]'
currency_zerovalue='([$][0]+)'

numerical_trailing_zeros='([.]\d+)[0]+'

numerical_leading_zeros='^0+'

period='[.]+(^[0-9])'

period_end='\w+$[.]+'

specialChar='[>|,|/|%|=|+|<|#|^|(|)|\'|:|;|`|\[|\]|?|\*]'

comma='[,]'

percentage='[%](\D)'

start_of_heading='\x01'

