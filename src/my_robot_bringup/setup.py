from setuptools import find_packages, setup

package_name = 'my_robot_bringup'

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
    maintainer_email='kirk@example.com',
    description='AI 倉庫搬運機器人 — 第一個 Embodied AI 作品',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_commander = my_robot_bringup.robot_commander:main',
            'robot_driver = my_robot_bringup.robot_driver:main',
            'warehouse_robot = my_robot_bringup.warehouse_robot:main',
            'task_sender = my_robot_bringup.task_sender:main',
            'warehouse_robot_ai = my_robot_bringup.warehouse_robot_ai:main',
            'task_sender_ai = my_robot_bringup.task_sender_ai:main',
        ],
    },
)
