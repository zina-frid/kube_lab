# Исследование возможностей отказоустойчивости приложений в Kubernetes
Проект в рамках курса "Методология разработки программного обеспечения DevOps"

## Описание

Данный проект представляет собой курсовую работу, посвящённую исследованию отказоустойчивости приложений, эксплуатируемых в Kubernetes. Основной задачей было оценить поведение приложения при уничтожении Pod'ов с использованием утилиты kubedoom. Работа включает как теоретическое исследование, так и практическую часть с экспериментами в реальном Kubernetes-кластере.

## Задание
1. Выбрать тестовое приложение, которое можно запустить в виде нескольких реплик (Pods). Это может быть как приложение, разработанное вами, так и, например, NGINX.
2. Изучить репозиторий [kubedoom](https://github.com/storax/kubedoom).
3. Установить Kubedoom в кластер Kubernetes.
4. Написать Deployment manifests для установки приложения.
5. Установить тестовое приложение в несколько реплик в кластер Kubernetes.
6. Подключиться к Kubedoom и сыграть в игру, убивая Pods запущенного приложения.

## Содержимое репозитория

- **Dockerfile**: Описание образа Docker для тестового приложения.
- **web_server.py**: Исходный код простого веб-сервера.
- **availability_test.py**: Скрипт для проверки доступности приложения во время эксперимента.
- **course-paper-manifests/**: YAML-файлы для установки приложения и kubedoom в Kubernetes.
- **exp_res.txt**: Текстовый файл с результатами эксперимента.
- **screens/**: Скриншоты процесса работы.
- **Записи экрана** во время эксперимента находятся на [диске](https://drive.google.com/drive/folders/1VqcuCw3IaPVtw4j6ePRywP895PkENoX1?usp=sharing).

## Запуск
Для выполнения экспериментов необходимо развернуть кластер Kubernetes с помощью Minikube. Пример запуска Minikube:

```bash
minikube start --cpus=2 --memory=3000 --nodes=3 --driver=kvm2
```
*Параметры:*

*`--cpus=2`— количество виртуальных процессоров, выделенных для кластера.*

*`--memory=3000` — объём оперативной памяти, выделенной для кластера (в МБ).*

*`--nodes=3` — количество узлов в многовузловом кластере.*

*`--driver=kvm2` — драйвер для управления виртуальными машинами (в данном случае KVM2).*

Запуск веб-приложения:
```bash
python web_server.py 
```
Приложение запустится, и к нему можно подключиться. Сервер доступен по адресу: http://localhost:8000. Отображаются все файлы в папке `course_paper`:

![Каталог проекта](/screens/web_server.png)

Запуск процесса сборки Docker-образ тестового приложения:
```bash
docker build -t simple-web-server .
```

После сборки образа, можно запустить контейнер:
```bash
docker run -d -p 8000:8000 simple-web-server
```
Сервер таже доступен по адресу: http://localhost:8000. В этот раз отображаются только файлы из докер образа:

![Каталог docker образа](/screens/web_docker.png)

Применение манифестов Kubernetes из каталога `course-paper-manifests/`:
```bash
cd course-paper-manifests/
kubectl apply -f web-deployment.yaml 
kubectl apply -f web-service.yaml 
kubectl apply -f kubedoom-service.yaml 
```
Если при при примении последнего манифеста появляется ошибка `Error from server (NotFound): error when creating "kubedoom-service.yaml": namespaces "kubedoom" not found`, то необходимо создать простраанство имен `kubedoom`:
```bash
kubectl create namespace kubedoom
```
---
Установка Kubedoom в кластер выполняется с использованием деплоймента из репозитория разработчика:
```bash
cd ..
cd kubedoom/
kubectl apply -k manifest/ 
```

Запуск интерфейса управления и Kubedoom:
```bash
minikube dashboard
```
![Дэшборд](screens/minikube%20dasboard%20worloads.png)


![Дэшборд2](/screens/minicube%20dasboard%20nodes.png)

Подключение к Kubedoom с помощью VNC-клиента:
```bash
vncviewer $(minikube ip):32222
```
При подключении ввести пароль, указанный в настройках kubedoom (по умолчанию — `idqd`).

После успешного подключения откроется окно Doom. 

![Kubedoom](/screens/kubedoom.png)

**Важно!** Для проведения эксперимента необходимо ввести читы на неуязвимость, бесконечные патроны и возможность проходить сквозь стены.

![Kubedoom_cheet](/screens/kubedoom%20action%20.png)


## Эксперименты

Запустите Dashboard Minikube и Doom для проведения экспериментов.
Запустите тест доступности приложения:
```bash
python availability_test.py
```

В течение 2 минут уничтожайте монстров в Doom. Каждое уничтожение монстра приводит к завершению одного Pod приложения.

Для проведения нового эксперимента переконфигурируйте число реплик приложения с помощью команды (замените `<число_реплик>` на нужное значение, например, 4 или 8):
```bash
kubectl scale --replicas=<число_реплик> deployment/web
```
Затем снова запустите `availability_test.py`, вернитесь в Doom и уничтожайте монстров.

Результаты теста доступности сохраняются в `exp_res.txt`.


## Результаты эксперимента

Описанный эксперимент был выполнен последовательно с различным числом требуемых реплик приложения: поочерёдно использовались значения 1, 2, 4. 8 и 16. Результаты представлены ниже:

| Число реплик приложения, шт | Доступность, % | Средняя частота запросов, запросов/сек |
|-----------------------------|----------------|----------------------------------------|
| 1                           | 62.57          | 748.22                                 |
| 2                           | 91.12          | 941.83                                 |
| 4                           | 99.44          | 956.80                                 |
| 8                           | 99.78          | 971.51                                 |
| 16                          | 99.83          | 985.19                                 |

Из результатов эксперимента можно установить, что для обеспечения довольно высокой доступности приложения достаточно 4 реплик приложения в условиях симулированной ситуации.

**Записи экрана** во время эксперимента находятся на [диске](https://drive.google.com/drive/folders/1VqcuCw3IaPVtw4j6ePRywP895PkENoX1?usp=sharing).

## Список использованных источников
1. https://doom.fandom.com/wiki/SPISPOPD
2. https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/#command-line-proxy
3. https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md
4. https://minikube.sigs.k8s.io/docs/handbook/accessing/
5. https://kubernetes.io/docs/tasks/access-application-cluster/service-access-application-cluster/
6. https://kubernetes.io/docs/concepts/services-networking/service/
