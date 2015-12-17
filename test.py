from PIL import Image
from StegosaurusImageLSB import StegosaurusImageLSB

   
#Get max data size
def test_get_max_size():
    original = Image.open('chameleon_1920x1276.png')
    st = StegosaurusImageLSB()
    print 'Max message size(chameleon_1920x1276.png): %d' % st.get_max_size(original)


#Inject data
def test_inject():
    original = Image.open('chameleon_1920x1276.png')
    st = StegosaurusImageLSB()
    msg = 'Do not forget to visit my blog: lopezezequiel.com'
    injected = st.inject(original, msg)
    injected.save('chameleon_1920x1276_injected.png')
    print 'Message injected in chameleon_1920x1276_injected.png: %s' % msg


#Extract data
def test_extract():
    injected = Image.open('chameleon_1920x1276_injected.png')
    st = StegosaurusImageLSB()
    msg = st.extract(injected)
    print 'Message extracted from chameleon_1920x1276_injected.png: %s' % msg


#Inject file
def test_inject_file():
    original = Image.open('chameleon_4912x3264.png')
    st = StegosaurusImageLSB()
    injected = st.inject_file(original, 'Alan Walker - Spectre.mp3')
    injected.save('chameleon_4912x3264_injected.png')
    print 'File injected in chameleon_4912x3264_injected.png: Alan Walker - Spectre.mp3'


#Extract file
def test_extract_file():
    injected = Image.open('chameleon_4912x3264_injected.png')
    st = StegosaurusImageLSB()
    st.extract_file(injected, 'tmp')
    print 'File extracted from chameleon_4912x3264_injected.png: ./tmp/Alan Walker - Spectre.mp3'


test_get_max_size()
test_inject()
test_extract()
test_inject_file()
test_extract_file()
