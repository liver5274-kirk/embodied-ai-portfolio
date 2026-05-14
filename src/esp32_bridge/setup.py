from setuptools import find_packages, setup

package_name = 'esp32_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Kirk',
    maintainer_email='liver5274@gmail.com',
    description='ROS2 bridge to ESP32 ROD car via WiFi HTTP',
    license='MIT',
    entry_points={
        'console_scripts': [
            'esp32_bridge = esp32_bridge.esp32_bridge:main',
        ],
    },
)
