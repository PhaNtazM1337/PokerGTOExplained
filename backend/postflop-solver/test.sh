cd python_lib
maturin build --release
pip3 install ./target/wheels/python_lib-0.1.0-cp312-cp312-macosx_11_0_arm64.whl --force-reinstall
cd ..
python3 main.py