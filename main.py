from views.theme import aplicar_tema
from views.login_view import LoginView
from models.login_model import LoginModel
from controllers.login_controller import LoginController

if __name__ == "__main__":
    aplicar_tema()

    app_view = LoginView()
    app_model = LoginModel()
    app_controller = LoginController(app_view)
    
    app_view.mainloop()