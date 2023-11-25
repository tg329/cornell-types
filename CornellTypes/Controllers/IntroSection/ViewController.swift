//
//  ViewController.swift
//  CornellTypes
//
//  Created by Alvaro Deras on 11/19/23.
//

import UIKit

class ViewController: UIViewController {

    // MARK: - Properties (view)
    
    private let cornell = UILabel()
    private let types = UILabel()
    private let logo = UIImageView()
    private let bear = UIImageView()
    private let subtitle = UILabel()
    private let login = UIButton()
    private let signup = UIButton()
    private let image = UIImageView()
    
    
    // MARK: - viewDidLoad
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.hack.white

        setupLogo()
        setupSubtitle()
        setupLogin()
        setupSignup()
    }

    // MARK: - Set Up Views
    
    private func setupLogo() {
        logo.image = UIImage(named: "cornellTypesLogo")
        
        view.addSubview(logo)
        logo.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            logo.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 28),
            logo.topAnchor.constraint(equalTo: view.topAnchor, constant: 151),
            logo.widthAnchor.constraint(equalToConstant: 346),
            logo.heightAnchor.constraint(equalToConstant: 187.9)
        ])
    }
    private func setupSubtitle() {
        subtitle.text = "lorem ipsum dolor."
        subtitle.textColor = UIColor.hack.red
        subtitle.font = UIFont(name: "Fredoka-Regular", size: 22)
        subtitle.numberOfLines = 0
        
        view.addSubview(subtitle)
        subtitle.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            subtitle.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            subtitle.topAnchor.constraint(equalTo: view.topAnchor, constant: 346)
        ])
    }
    
    private func setupLogin() {
        login.setTitle("log in", for: .normal)
        login.titleLabel!.font = UIFont(name: "Fredoka-Medium", size: 22)
        login.setTitleColor(UIColor.hack.white, for: .normal)
        login.setBackgroundImage(UIImage(named: "tanrect"), for: .normal)
        login.layer.cornerRadius = 16
        login.addTarget(self, action: #selector(pushLogin), for: .touchUpInside)
        
        view.addSubview(login)
        login.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            login.topAnchor.constraint(equalTo: view.topAnchor, constant: 426),
            login.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 64),
            login.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -68),
            login.widthAnchor.constraint(equalToConstant: 243),
            login.heightAnchor.constraint(equalToConstant: 50)
        ])
    }
    
    private func setupSignup() {
        signup.setTitle("sign up", for: .normal)
        signup.titleLabel!.font = UIFont(name: "Fredoka-Medium", size: 22)
        signup.setTitleColor(UIColor.hack.white, for: .normal)
        signup.setBackgroundImage(UIImage(named: "tanrect"), for: .normal)
        signup.layer.cornerRadius = 16
        signup.addTarget(self, action: #selector(pushSignup), for: .touchUpInside)
        
        view.addSubview(signup)
        signup.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            signup.topAnchor.constraint(equalTo: view.topAnchor, constant: 503),
            signup.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 64),
            signup.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -68),
            signup.widthAnchor.constraint(equalToConstant: 243),
            signup.heightAnchor.constraint(equalToConstant: 50)
        ])
    }
    
    @objc private func pushLogin() {
        let vc = LoginVC()
        navigationController?.pushViewController(vc, animated: true)
    }
    
    @objc private func pushSignup() {
        let vc = SignupVC()
        navigationController?.pushViewController(vc, animated: true)
    }
}
