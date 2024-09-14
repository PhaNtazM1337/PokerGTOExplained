cd python_lib
maturin build --release
cd ..
pip3 install /Users/arararz/Documents/GitHub/postflop-solver/python_lib/target/wheels/python_lib-0.1.0-cp312-cp312-macosx_11_0_arm64.whl --force-reinstall
python3 main.py