git clone --filter=blob:none --sparse https://github.com/misilelab/misilelib.git
cd misilelib
git sparse-checkout init --cone
git sparse-checkout add misilelib-python
cd -

