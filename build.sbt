val scala3Version = "3.3.0"

lazy val root = project
  .in(file("."))
  .settings(
    name := "wikigame",
    version := "0.1.0-SNAPSHOT",

    scalaVersion := scala3Version,

    libraryDependencies += "org.scalameta" %% "munit" % "0.7.29" % Test,
    libraryDependencies += "com.softwaremill.sttp.client4" %% "core" % "4.0.0-M5"
  )
