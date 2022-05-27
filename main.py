from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
import cv2
import os
from playsound import playsound


def log_decorator(func):
    def wrap():
        print(f'Starting function {func}')
        func()
        print(f'Finished function {func}')

    return wrap


def image_comparing(img1, img2):
    featurescount = 1000  # кол-во точек
    orb = cv2.ORB_create(nfeatures=featurescount)  # инициализируем 1000 контрольных точек

    kp1, des1 = orb.detectAndCompute(img1, None)  # получаем контрольные точки и их дескрипторы
    kp2, des2 = orb.detectAndCompute(img2, None)

    bruteforce = cv2.BFMatcher()
    matches = bruteforce.knnMatch(des1, des2, k=2)
    # сравниваем дескрипторы 1-го изображения со дескрипторами 2-го (k=2 - получаем 2 лучших нахождения)

    good = []
    for m, n in matches:
        # print(f"m = {m.distance}, n = {n.distance}")
        # если m и n (2 лучших совпадения) отличаются >25%, значит это хорошее нахождение, заносим его в итоговый массив
        if m.distance < 0.75 * n.distance:
            good.append([m])

    # img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
    # cv2.imshow(img3)

    return round(len(good) / featurescount, 2)


class CameraScreen(Screen):
    is_first_enter = False
    first_x = 0


class LibraryScreen(Screen):
    firstenter = False
    first_x = 0

    def on_enter(self, *args):
        print("Entered Library")
        self.firstenter = True


class ScreenManager(ScreenManager):
    def ScreenChange(self, ScreenName):
        self.current = ScreenName


class AnchorLayoutExample(AnchorLayout):
    pass


class ScrollViewPacks(ScrollView):
    pass


class FolderButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'FolderButton'
    def on_release(self):
        myroot = self.get_root_window()
        print(f'height = {myroot.height}')
        print(f'min height = {myroot.minimum_height}')


class CreateNewFolderButton(Button):
    def on_release(self):
        myroot = self.get_root_window()
        print(f'height = {myroot.height}')
        print(f'min height = {myroot.minimum_height}')


class SoundPackCheckBox(Switch):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'SoundPackCheckBox'

    def on_active(self, *args, **kwargs):
        # Switch value are True and False
        if self.active:
            stacklayout_packs_children = self.parent.parent.children
            for box in stacklayout_packs_children:
                if box.name == 'ASS':
                    boxchildren = [child for child in box.children if child.name == 'SoundPackCheckBox']
                    if boxchildren[0] != self:
                        boxchildren[0].active = False
        else:
            print('Switch is OFF')


class SoundPackBox(BoxLayout):
    def __init__(self, name, height_ration, **kwargs):
        super().__init__(**kwargs)

        self.name = "ASS"

        self.orientation = 'vertical'
        self.add_widget(SoundPackCheckBox(text=name, size_hint=(1, .2)))
        button_folder = FolderButton(text=name, size_hint=(1, .8))
        self.add_widget(button_folder)
        self.size_hint = (0.5, height_ration)


class StackLayoutPacks(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'StackLayoutPacks'
        directory_with_samples = 'ImagesSamples'
        folders_libraries = [name for name in os.listdir(directory_with_samples) if
                             os.path.isdir(f'{directory_with_samples}\\{name}')]
        self.has_created_folders = True

        self.blocks_count = len(folders_libraries)
        if self.blocks_count == 0:
            self.has_created_folders = False
            self.blocks_count = 1

        self.horizontal_blocks_count = 2
        self.total_height = self.height * self.blocks_count
        self.folder_button_height_ratio = round(1 / 0.5 / (self.blocks_count + self.blocks_count % 2), 5)

        if self.has_created_folders:
            for i in range(self.blocks_count):
                # button_folder = FolderButton(text=folders_libraries[i], size_hint=(0.5, self.folder_button_height_ratio))
                # self.add_widget(button_folder)
                soundpackbox = SoundPackBox(folders_libraries[i], self.folder_button_height_ratio)
                self.add_widget(soundpackbox)
            TheLabApp.active_pack_id = 1

        else:
            button_folder = CreateNewFolderButton(text="Add new group",
                                                  size_hint=(0.5, self.folder_button_height_ratio))
            self.add_widget(button_folder)


class GridLayoutExample(GridLayout):
    counter = 0
    text = StringProperty("Ha!")

    cap = cv2.VideoCapture(0)
    cap.open(0)
    imagecapture = 'ImagesSamples/unnamed.jpg'
    if cap.isOpened():
        # pass
        # while True:
        try:
            success, imagecapture = cap.read()
            if not success:
                imagecapture = 'ImagesSamples/unnamed.jpg'
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        except Exception:
            imagecapture = 'ImagesSamples/unnamed.jpg'
            print('Не удалось найти камеру')
    else:
        print('Не смог открыть камеру')

    # cap.release()
    # cv2.destroyAllWindows()

    # @log_decorator
    def on_button_camera_release(self):
        self.counter += 1
        self.text = f"{self.counter}"
        print('button1')
        img1 = cv2.imread('ImageForRecognition/template-sheeeit.png')
        directory_with_samples = 'ImagesSamples'
        all_images = [file for file in os.listdir(directory_with_samples) if os.path.isdir(file) == False]

        # images_comparing_results = dict([(img_sample, image_comparing(img1, cv2.imread(f'{directory_with_samples}//{img_sample}'))) for i, img_sample in enumerate(all_images)])
        images_comparing_results = []
        for img_sample in all_images:
            try:
                img2 = cv2.imread(f'{directory_with_samples}/{img_sample}')

            except Exception:
                print('Error while reading image')
            else:
                images_comparing_results.append(image_comparing(img1, img2))

        images_comparing_results = dict(zip(all_images, images_comparing_results))

        best_match_image = max(images_comparing_results, key=images_comparing_results.get)
        print(best_match_image)
        # playsound("SoundSamples/di.wav")

    def on_switch_callback(self, switchObject, switchValue):

        # Switch value are True and False
        if (switchValue):
            print('Switch is ON:):):)')
        else:
            print('Switch is OFF:(:(:(')


class BoxLayoutExample(BoxLayout):
    pass


class GridLayoutLibrary(GridLayout):
    def on_button_release(self):
        print('button')
        directory_with_samples = 'ImagesSamples'
        img_sample = 'sheeeit.png'
        img2 = cv2.imread(f'{directory_with_samples}/{img_sample}')
        App.get_running_app().change_screen(screen_name="LocalLibraryScreen", direction="left")


class LocalLibraryScreen(Screen):
    def __init__(self, **kwargs):
        super(LocalLibraryScreen, self).__init__(**kwargs)
        # self.add_widget(Button(text="Ass", size_hint=(.5, .5)))
        # self.add_widget(Button(text="Ass2", size_hint=(.5, .5)))

    def on_button_back_release(self):
        App.get_running_app().change_screen(screen_name="LibraryScreen", direction="right")


class MainWidget(Widget):
    pass


class TheLabApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_pack_id = None

    def build(self):
        pass
        # ScreenManager.add_widget(CameraScreen(name='CameraScreen'))
        # ScreenManager.add_widget(LocalLibraryScreen(name='LocalLibraryScreen'))
        # for key, val in self.root.ids.items():
        #    print("key={0}, val={1}".format(key, val))
        # carousel = Carousel(direction='right')
        # for i in range(10):
        #    src = "http://placehold.it/480x270.png&text=slide-%d&.png" % i
        #    image = AsyncImage(source=src, allow_stretch=True)
        #    carousel.add_widget(image)
        # return carousel

    def change_screen(self, screen_name, direction):
        screen_manager = self.root.ids.ScreenManager
        screen_manager.current = screen_name
        screen_manager.transition.direction = direction

    def on_touch_down(self, touch):
        print('touch')


TheLabApp().run()
